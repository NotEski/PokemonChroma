# Move Tag System Gaps and Enhancement Opportunities

## Overview

The Advanced AI System uses a tag-based move categorization system inherited from the move repository. This document outlines gaps between the Ruby system (which uses rich move metadata) and the current Python tag system, along with recommendations for future enhancements.

## Current Tag System

### Implemented Tags

The following tags are currently available and used by the AI:

| Tag | Purpose | AI Usage |
|-----|---------|----------|
| `HealMove` | Healing moves | Healing move scoring, prioritization |
| `SetupMove` | Stat-boosting setup moves | Setup detection, threat assessment |
| `StatChangeMove` | Any stat modification | Setup recognition, counter-play |
| `FlinchMove` | Flinch/paralysis inducing | Priority assessment |
| `DrainMove` | Damage with heal portion | Recoil vs recovery evaluation |
| `RecoilMove` | Damage with self-harm | Recoil damage penalty |
| `HazardMove` | Entry hazard setup | Field effects analysis |
| `HazardRemovalMove` | Hazard removal (Rapid Spin, etc) | Field effects, support role |
| `ScreenMove` | Screen setup (Reflect, Light Screen) | Support role detection, defensive play |
| `StatusMove` | Status condition infliction | Status move scoring |
| `SwitchOutMove` | Forced switch moves | Switch-in analysis |
| `CriticalHitMove` | High crit rate moves | Critical hit factor in scoring |
| `WeatherMove` | Weather setup moves | Field effects integration |
| `TerrainMove` | Terrain setup moves | Field effects integration |

### Usage Pattern

```python
# Check if move has tag
if move.has_tag("SetupMove"):
    # Treat as setup move
    
# Multiple tags can apply to same move
# Move scoring considers all applicable tags
```

## Identified Gaps

### Gap 1: Multi-Stat Setup Moves

**Problem**: Setup moves that boost multiple stats can only be tagged as `SetupMove` generically. No way to distinguish:
- Single stat boosters (Swords Dance: +Atk only)
- Dual stat boosters (Dragon Dance: +Atk, +Spe)
- Triple stat boosters (Calm Mind: +SpA, +SpD)
- Stat-specific boosts

**Current Workaround**: Move scorer estimates sweep potential by checking opponent stats, but this is imprecise.

**Recommendation**: Add multi-value tag support or extended tags:
```
SetupMove:MultiStat  # Indicates multiple stats
SetupMove:Offensive  # +Atk or +SpA focus
SetupMove:Speed     # Includes speed boost
SetupMove:Defensive # +Def or +SpD focus
```

**Impact**: Medium - Affects setup threat scoring accuracy
**Implementation Priority**: Medium - Consider for v2

---

### Gap 2: Weather-Dependent Move Effects

**Problem**: Moves with weather-dependent effects/healing:
- Synthesis (Heal varies: 50% → 66% in sun, 25% in rain/hail/sand)
- Moonlight (Heal varies: 50% → 66% at night)
- Weather Ball (Type/power varies by weather)
- Solar Beam (Can't use in weather, delayed in non-sun)

**Current Workaround**: Healing moves always scored as 50% recovery, no weather consideration.

**Recommendation**: Implement weather context in move scoring:
```python
def _get_weather_dependent_effect(move, weather):
    if move.name == "Synthesis":
        return {"sun": 0.66, "default": 0.50, "rain": 0.25}[weather]
```

**Impact**: Low-Medium - Rare but significant in weather teams
**Implementation Priority**: Low - Weather matchup detection exists, just not used for move scoring

---

### Gap 3: Protect Variant Effects

**Problem**: Protect move variants have different mechanics not captured by tags:
- Protect (blocks turn)
- Detect (blocks turn, identical effect)
- Endure (survive 1 turn at 1 HP instead of blocking)
- King's Shield (blocks + lowers opponent Atk)
- Spiky Shield (blocks + damages on contact)

**Current Workaround**: All treated as generic protective moves, no distinction for stat-changing variants.

**Recommendation**: Add sub-tags for Protect variants:
```
ProtectMove           # Base tag
ProtectMove:Stat      # Also changes stats (King's Shield, Spiky Shield)
ProtectMove:Endure    # Survives at 1 HP instead of protecting
```

**Impact**: Low - Protect usage is situational, mostly same value
**Implementation Priority**: Low - Not critical for core AI

---

### Gap 4: Hazard Removal Identification

**Problem**: Moves that remove hazards are not specifically tagged:
- Rapid Spin (removes hazards + entry hazard blocker)
- Defog (clears terrain + hazards + screens)
- Court Change (swaps field effects)

**Current Workaround**: Only `HazardRemovalMove` tag, all treated identically.

**Recommendation**: Extend hazard removal categorization:
```
HazardRemovalMove         # Base tag
HazardRemovalMove:Defog   # Also removes terrain
HazardRemovalMove:Defog   # Also clears screens
HazardRemovalMove:Spin    # Hits + removes
```

**Impact**: Low-Medium - Affects support role detection
**Implementation Priority**: Low-Medium - Enhancement for role detection accuracy

---

### Gap 5: Spread Move Identification

**Problem**: Moves that hit multiple targets aren't explicitly identified:
- Earthquake/Surf (hits all except user)
- Dazzling Gleam (hits all others)
- Earthquake in Doubles (hits all except user)

**Current Workaround**: Not currently handled, moves assumed single-target.

**Recommendation**: Add spread move tag:
```
SpreadMove            # Hits multiple targets
SpreadMove:All        # Hits all but user
SpreadMove:Allies     # Hits ally (Helping Hand, etc)
SpreadMove:Partner    # Hits partner only (Doubles-specific)
```

**Impact**: Low - Doubles/Triples AI not fully implemented yet
**Implementation Priority**: Very Low - Future implementation for multi-battle formats

---

### Gap 6: OHKO Move Explicit Tagging

**Problem**: One-hit KO moves aren't explicitly categorized:
- Horn Drill
- Guillotine
- Sheer Cold
- Horn Drill (varies by level difference)

**Current Workaround**: Treated as high-power moves, no special OHKO consideration.

**Recommendation**: Add explicit OHKO tag:
```
OHKOMove              # Attempts guaranteed KO
OHKOMove:Accuracy    # Subject to accuracy checks
```

**Impact**: Very Low - OHKOs are rare and usually low-priority
**Implementation Priority**: Very Low - Nice-to-have for edge cases

---

### Gap 7: Move Accuracy Variations

**Problem**: Some moves have accuracy that varies by condition:
- Swift/Aura Sphere (never miss)
- Thunder (85% → 100% in rain)
- Blizzard (70% → 100% in hail)
- Stone Edge (80% accuracy)

**Current Workaround**: Accuracy penalty applied uniformly, no weather consideration.

**Recommendation**: Enhanced accuracy handling:
```python
def get_move_accuracy(move, weather=None, terrain=None):
    if move.name == "Thunder" and weather == "rain":
        return 1.0  # 100% effective
    return move.accuracy / 100.0
```

**Impact**: Low - Existing system is adequate for most scenarios
**Implementation Priority**: Low - Consider for v2 enhancement

---

### Gap 8: Stat Change Amounts

**Problem**: Stat-changing moves don't indicate boost amount:
- Single stage: Swords Dance (+1 Atk)
- Multiple stages: Tail Dance (+1 Atk, +1 SpA, +1 Spe) or Power-Up Punch (+1 Atk)
- No negative vs positive indication

**Current Workaround**: Setup detection counts boost stages, but can't differentiate between single +1 and triple +1 moves.

**Recommendation**: Extend with stage count tags:
```
StatChangeMove:Plus1   # Single stage boost
StatChangeMove:Plus2   # Double stage boost
StatChangeMove:Multi   # Multiple different stats boosted
StatChangeMove:Minus   # Negative to self or positive to opponent stats
```

**Impact**: Medium - Affects setup threat scoring
**Implementation Priority**: Medium - Consider for v2

---

## Enhancement Roadmap

### Phase 1: High Impact (v1.5)
- [ ] Multi-stat setup move categorization (Gap 1)
- [ ] Stat change amount specification (Gap 8)
- [ ] Enhanced hazard removal tagging (Gap 4)

### Phase 2: Medium Impact (v2.0)
- [ ] Weather-dependent move effects (Gap 2)
- [ ] Protect variant sub-tags (Gap 3)
- [ ] Move accuracy weather variations (Gap 7)

### Phase 3: Low Impact / Format-Specific (v2.5+)
- [ ] Spread move identification (Gap 5) - for Doubles/Triples support
- [ ] OHKO move explicit tagging (Gap 6) - edge case handling
- [ ] Dynamic accuracy calculation (Gap 7) - refinement

## Implementation Guidance

### How to Add Tags to Move Repository

Tags are defined in the move repository (external to this AI system). To add new tags:

1. **Location**: `engine/repositories/moves/` (move definitions)
2. **Pattern**:
   ```python
   move.add_tag("SetupMove")
   move.add_tag("StatChangeMove:Plus1")  # For new sub-tags
   ```

3. **AI Integration**: Once tags exist, add scoring logic:
   ```python
   # In move_scorer.py _score_setup_move()
   if move.has_tag("StatChangeMove:Multi"):
       score += 15  # Bonus for multi-stat boosts
   ```

### Testing Tag Implementations

```python
# Verify tag exists
assert move.has_tag("SetupMove")

# Test move scoring with new tags
context = AIContext(battle_manager, position)
score = move_scorer.score_move(context, move)
assert score > base_score  # Should improve with better tagging
```

## Current Workarounds Summary

| Gap | Workaround | Limitation |
|-----|-----------|-----------|
| Multi-stat setup | Count stat stages from opponent | Imprecise for sweep potential |
| Weather healing | Assume 50% recovery | Inaccurate in weather teams |
| Protect variants | All scored identically | Stat-changing variants undervalued |
| Hazard removal | Generic tag | Can't distinguish Rapid Spin vs Defog |
| Spread moves | Not handled | Would affect Doubles AI |
| OHKO moves | High power moves | Incorrect scoring |
| Move accuracy | Uniform penalty | Misses weather-dependent moves |
| Stat changes | Count stages | Can't differentiate boost amounts |

## Conclusion

The tag system is **adequate for current AI needs** (singles, core features). Gaps are primarily in:
- **Precision**: Workarounds function but are less accurate
- **Format Support**: Doubles/Triples would need additional tags
- **Future Enhancement**: v2.0+ should address highest-impact gaps

**Recommendation**: Focus v1.0 implementation on current capabilities. Revisit Gap 1 and Gap 8 in v1.5 if move scoring needs refinement.

## References

- Move Repository: `engine/repositories/moves/`
- Move Scoring: `move_scorer.py`
- Tag Usage: Search codebase for `has_tag()` calls
- Ruby Reference: `AdvancedAI/Advanced AI System/[003] Move_Scorer.rb`
