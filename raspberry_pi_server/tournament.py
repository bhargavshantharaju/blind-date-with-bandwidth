"""
Tournament mode: support for multi-station (up to 8) competitive bracket.
Handles pairing, tournament progression, leaderboard.
"""

import json
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class TournamentRound(Enum):
    """Tournament rounds."""
    QUALIFICATION = "qualification"
    ROUND_1 = "round_1"
    ROUND_2 = "round_2"
    ROUND_3 = "round_3"
    FINAL = "final"


@dataclass
class Match:
    """Single match between two stations."""
    match_id: str
    pair_id: int
    station_a: str
    station_b: str
    round_num: TournamentRound
    track_a: int = 0
    track_b: int = 0
    sync_time_ms: int = 0
    winner: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed
    timestamp: float = field(default_factory=time.time)


@dataclass
class Leaderboard:
    """Track station performance."""
    station_id: str
    matches_played: int = 0
    matches_won: int = 0
    fastest_sync_ms: float = float('inf')
    avg_sync_ms: float = 0.0
    total_sync_ms: int = 0


class TournamentBracket:
    """Manage single-elimination tournament bracket."""
    
    def __init__(self, num_stations: int = 8):
        """
        Args:
            num_stations: 2, 4, or 8 stations (2^n)
        """
        if num_stations not in [2, 4, 8]:
            raise ValueError("Must have 2, 4, or 8 stations")
        
        self.num_stations = num_stations
        self.num_rounds = {2: 1, 4: 2, 8: 3}[num_stations]
        self.stations = [f"STATION_{i}" for i in range(num_stations)]
        self.matches: List[Match] = []
        self.leaderboard: Dict[str, Leaderboard] = {
            s: Leaderboard(station_id=s) for s in self.stations
        }
        self.current_round = TournamentRound.ROUND_1
        self.lock = threading.Lock()
    
    def generate_pairings(self) -> List[Tuple[str, str]]:
        """Generate random station pairings for current round."""
        available = self.stations.copy()
        random.shuffle(available)
        
        pairs = []
        for i in range(0, len(available), 2):
            pairs.append((available[i], available[i + 1]))
        
        return pairs
    
    def start_round(self, round_num: TournamentRound):
        """Start a new tournament round."""
        with self.lock:
            self.current_round = round_num
            pairs = self.generate_pairings()
            
            for pair_id, (station_a, station_b) in enumerate(pairs):
                match = Match(
                    match_id=f"{round_num.value}_{pair_id}",
                    pair_id=pair_id,
                    station_a=station_a,
                    station_b=station_b,
                    round_num=round_num
                )
                self.matches.append(match)
                logger.info(f"Match created: {station_a} vs {station_b} in {round_num.value}")
    
    def record_match_result(self, match_id: str, station_a_track: int, station_b_track: int, sync_time_ms: int):
        """Record result of a match."""
        with self.lock:
            match = next((m for m in self.matches if m.match_id == match_id), None)
            if not match:
                logger.error(f"Match not found: {match_id}")
                return
            
            match.track_a = station_a_track
            match.track_b = station_b_track
            match.status = "completed"
            match.sync_time_ms = sync_time_ms
            
            if station_a_track == station_b_track:
                match.winner = match.station_a if random.random() < 0.5 else match.station_b
                
                # Update leaderboard
                self.leaderboard[match.station_a].matches_played += 1
                self.leaderboard[match.station_b].matches_played += 1
                
                self.leaderboard[match.winner].matches_won += 1
                self.leaderboard[match.winner].fastest_sync_ms = min(
                    self.leaderboard[match.winner].fastest_sync_ms,
                    sync_time_ms
                )
                self.leaderboard[match.winner].total_sync_ms += sync_time_ms
                
                logger.info(f"Match completed: {match.winner} won in {sync_time_ms}ms")
                return match.winner
            
            return None
    
    def get_winners(self) -> List[str]:
        """Get winners of current round."""
        round_winners = [m.winner for m in self.matches if m.round_num == self.current_round and m.winner]
        return round_winners
    
    def advance_to_next_round(self) -> bool:
        """Advance winners to next round."""
        if self.current_round == TournamentRound.FINAL:
            return False
        
        round_map = {
            TournamentRound.ROUND_1: TournamentRound.ROUND_2,
            TournamentRound.ROUND_2: TournamentRound.ROUND_3,
            TournamentRound.ROUND_3: TournamentRound.FINAL,
        }
        
        next_round = round_map.get(self.current_round)
        if next_round:
            self.stations = self.get_winners()
            self.start_round(next_round)
            return True
        
        return False
    
    def get_leaderboard_json(self) -> str:
        """Serialize leaderboard to JSON."""
        board_list = []
        for station, stats in sorted(
            self.leaderboard.items(),
            key=lambda x: x[1].matches_won,
            reverse=True
        ):
            avg_sync = stats.total_sync_ms / max(stats.matches_won, 1)
            board_list.append({
                'station': station,
                'matches_won': stats.matches_won,
                'matches_played': stats.matches_played,
                'fastest_sync_ms': stats.fastest_sync_ms if stats.fastest_sync_ms != float('inf') else 0,
                'avg_sync_ms': int(avg_sync)
            })
        
        return json.dumps(board_list)


class NeoPixelColors:
    """Color definitions for pair identification."""
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)
    CYAN = (0, 255, 255)
    ORANGE = (255, 165, 0)
    WHITE = (255, 255, 255)
    
    PAIR_COLORS = [RED, BLUE, GREEN, YELLOW, PURPLE, CYAN, ORANGE, WHITE]


# Reference ESP32 code for tournament mode:
NEOPIXEL_SKETCH = """
#include <Adafruit_NeoPixel.h>

#define NEOPIXEL_PIN 33
#define NUM_PIXELS 1  // One LED per station

Adafruit_NeoPixel pixels(NUM_PIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

// Pair colors (from pair_id)
uint8_t pair_colors[8][3] = {
  {255, 0, 0},    // Red - Pair 1
  {0, 0, 255},    // Blue - Pair 2
  {0, 255, 0},    // Green - Pair 3
  {255, 255, 0},  // Yellow - Pair 4
  {255, 0, 255},  // Purple - Pair 5
  {0, 255, 255},  // Cyan - Pair 6
  {255, 165, 0},  // Orange - Pair 7
  {255, 255, 255} // White - Pair 8
};

void setPairColor(int pair_id) {
  uint8_t* color = pair_colors[pair_id % 8];
  pixels.setPixelColor(0, pixels.Color(color[0], color[1], color[2]));
  pixels.show();
}

void displayRound(int round_num) {
  // Pulse effect to indicate round progression
  for (int brightness = 0; brightness < 256; brightness += 10) {
    pixels.setBrightness(brightness);
    pixels.show();
    delay(10);
  }
  for (int brightness = 255; brightness > 0; brightness -= 10) {
    pixels.setBrightness(brightness);
    pixels.show();
    delay(10);
  }
}

// In setup():
pixels.begin();
pixels.show();

// Usage:
setPairColor(pair_id);  // Set LED to pair color
displayRound(round_num);  // Pulse to indicate round start
"""

print("NeoPixel tournament reference added")
