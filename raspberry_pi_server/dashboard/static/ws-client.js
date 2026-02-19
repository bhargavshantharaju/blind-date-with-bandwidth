/**
 * Shared WebSocket client module for all Blind Date frontends.
 * Handles connection, event routing, reconnection, and offline queueing.
 * 
 * Usage:
 *   import { WebSocketClient } from './ws-client.js';
 *   const client = new WebSocketClient();
 *   client.on('matched', (data) => console.log('Matched!', data));
 *   client.connect();
 */

class WebSocketClient {
    constructor(url = null) {
        this.url = url || `ws://${window.location.host}/socket.io`;
        this.socket = null;
        this.handlers = {}; // event type -> [callbacks]
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // ms, exponential backoff
        this.offlineQueue = []; // Queue for actions when disconnected
        this.eventHistory = [];
        this.maxHistorySize = 100;
    }

    /**
     * Connect to WebSocket server.
     */
    connect() {
        try {
            this.socket = io(this.url, {
                reconnection: true,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: 10000,
                reconnectionAttempts: this.maxReconnectAttempts
            });

            this.socket.on('connect', () => {
                console.log('[WebSocket] Connected');
                this.connected = true;
                this.reconnectAttempts = 0;
                this._setConnectionIndicator(true);
                this._processOfflineQueue();
                this._emit('connected', {});
            });

            this.socket.on('disconnect', () => {
                console.log('[WebSocket] Disconnected');
                this.connected = false;
                this._setConnectionIndicator(false);
                this._emit('disconnected', {});
            });

            this.socket.on('event', (data) => {
                this._handleEvent(data);
            });

            this.socket.on('event_history', (events) => {
                console.log(`[WebSocket] Received ${events.length} history events`);
                events.forEach(e => this._handleEvent(e));
            });

            this.socket.on('error', (error) => {
                console.error('[WebSocket] Error:', error);
                this._emit('error', { message: error });
            });

        } catch (error) {
            console.error('[WebSocket] Connection failed:', error);
        }
    }

    /**
     * Disconnect from WebSocket server.
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }

    /**
     * Register handler for event type.
     * Example: client.on('matched', (data) => {...})
     */
    on(eventType, callback) {
        if (!this.handlers[eventType]) {
            this.handlers[eventType] = [];
        }
        this.handlers[eventType].push(callback);
    }

    /**
     * Route incoming event to registered handlers.
     * @private
     */
    _handleEvent(data) {
        const { type, timestamp, data: eventData } = data;
        
        // Store in history
        this.eventHistory.push(data);
        if (this.eventHistory.length > this.maxHistorySize) {
            this.eventHistory.shift();
        }

        console.log(`[WebSocket] Event: ${type}`);

        // Call registered handlers
        if (this.handlers[type]) {
            this.handlers[type].forEach(callback => {
                try {
                    callback(eventData, timestamp);
                } catch (error) {
                    console.error(`[WebSocket] Handler error for ${type}:`, error);
                }
            });
        }
    }

    /**
     * Internal: emit internal events.
     * @private
     */
    _emit(type, data) {
        if (this.handlers[type]) {
            this.handlers[type].forEach(callback => callback(data));
        }
    }

    /**
     * Queue action for when connection is restored.
     * @private
     */
    async _queueAction(action) {
        if (!this.connected) {
            console.log('[WebSocket] Queueing action for offline mode');
            this.offlineQueue.push(action);
            return false;
        }
        return true;
    }

    /**
     * Process queued actions after reconnection.
     * @private
     */
    _processOfflineQueue() {
        while (this.offlineQueue.length > 0) {
            const action = this.offlineQueue.shift();
            console.log('[WebSocket] Processing queued action:', action.type);
            if (action.callback) {
                action.callback();
            }
        }
    }

    /**
     * Update connection indicator UI element.
     * Expects element with id="ws-indicator"
     * @private
     */
    _setConnectionIndicator(connected) {
        const indicator = document.getElementById('ws-indicator');
        if (indicator) {
            indicator.innerHTML = connected 
                ? '<span style="color:green">●</span> Live'
                : '<span style="color:red">●</span> Reconnecting...';
        }
    }

    /**
     * Send command/action (requires connected state).
     */
    async sendAction(action, data = {}) {
        if (!this.connected) {
            const success = await this._queueAction({
                type: action,
                data,
                callback: () => this.socket.emit(action, data)
            });
            return !success;
        }
        this.socket.emit(action, data);
        return true;
    }

    /**
     * Get last N events from history.
     */
    getRecentEvents(count = 10) {
        return this.eventHistory.slice(-count);
    }

    /**
     * Get all events from history.
     */
    getAllHistory() {
        return [...this.eventHistory];
    }

    /**
     * Clear event history.
     */
    clearHistory() {
        this.eventHistory = [];
    }

    /**
     * Check connection status.
     */
    isConnected() {
        return this.connected;
    }

    /**
     * Get number of queued offline actions.
     */
    getQueueSize() {
        return this.offlineQueue.length;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketClient;
}
