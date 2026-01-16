"""
Advanced AI Orchestrator

Main AI class that coordinates all intelligence modules and makes battle decisions.

Ported from Advanced AI System core orchestration logic.
"""

from typing import TYPE_CHECKING, Optional, Tuple, List
from uuid import UUID, uuid4

from shared.pokemon.move_tags import HealMove, ScreenMove, StatChangeMove
from shared.battle.weather import BattleWeather
from shared.battle.terrain import BattleTerrain

from .settings import AISettings, FEATURE_GATES
from .ai_context import AIContext, AIBattleState
from .move_scorer import MoveScorer
from .threat_assessment import ThreatAssessment
from .switch_intelligence import SwitchIntelligence
from .setup_recognition import SetupRecognition
from .endgame_scenarios import EndgameScenarios
from .prediction_system import PredictionSystem
from .role_detection import RoleDetection
from .field_effects import FieldEffects
from .move_memory import MoveMemory
from .battle_personalities import BattlePersonalities, AIPersonality

if TYPE_CHECKING:
    from shared.battle.battle_actions import BattleAction, MoveAction, SwitchAction
    from shared.pokemon.pokemon import BattleMon
    from shared.pokemon.move import BaseMove, Move
    from shared.battle.position import BattlePosition


class AdvancedAI:
    """
    Main Advanced AI class that orchestrates battle decisions.
    
    Coordinates:
    - Move scoring and selection
    - Threat assessment
    - Switching decisions
    - Setup threat detection
    - Endgame optimization
    - Move prediction
    - Role detection
    - Field effects analysis
    - Battle personalities (optional)
    
    Implements skill-level gating for feature availability.
    """
    
    def __init__(
        self,
        settings: AISettings,
        personality: AIPersonality = AIPersonality.BALANCED,
    ) -> None:
        """
        Initialize Advanced AI.
        
        Args:
            settings: AI settings (skill level, features)
            personality: Battle personality (affects decision-making)
        """
        self.settings: AISettings = settings
        self.skill_level: int = settings.skill_level
        self.personality: BattlePersonalities = BattlePersonalities(personality)
        self.battler_id: UUID = uuid4()
        
        # Intelligence modules
        self.move_scorer: MoveScorer = MoveScorer()
        self.threat_assessment: ThreatAssessment = ThreatAssessment()
        self.switch_intelligence: SwitchIntelligence = SwitchIntelligence()
        self.setup_recognition: SetupRecognition = SetupRecognition()
        self.endgame_scenarios: EndgameScenarios = EndgameScenarios()
        self.prediction_system: PredictionSystem = PredictionSystem()
        self.role_detection: RoleDetection = RoleDetection()
        self.field_effects: FieldEffects = FieldEffects()
        self.move_memory: MoveMemory = MoveMemory()
    
    def choose_action(
        self,
        battle_state: AIBattleState,
    ) -> BattleAction:
        """
        Choose an action for the current battle position.
        
        Main decision orchestrator that considers all factors:
        1. Creates AI context from battle state
        2. Evaluates threat level
        3. Checks for endgame scenarios
        4. Checks for setup threats
        5. Evaluates switching options
        6. Scores available moves
        7. Applies personality modifiers
        8. Returns best action
        
        Args:
            battle_state: AIBattleState with current battle information
            
        Returns:
            BattleAction (MoveAction or SwitchAction)
        """
        
        # Create AI context from state
        context: AIContext = AIContext(state=battle_state)
        
        # Get threat assessment
        threat_level: float = self.threat_assessment.calculate_threat(context)
        
        # Evaluate endgame scenarios (skill_level >= 60)
        if self.skill_level >= 60:
            if self.endgame_scenarios.is_endgame_scenario(context):
                endgame_action: Optional[BattleAction] = self._evaluate_endgame_action(
                    context
                )
                if endgame_action is not None:
                    return endgame_action
        
        # Evaluate setup threats (skill_level >= 55)
        if self.skill_level >= 55:
            setup_threat: Optional[BattleAction] = self._evaluate_setup_threat(context)
            if setup_threat is not None:
                return setup_threat
        
        # Check if switching is beneficial (skill_level >= 50)
        if self.skill_level >= 50:
            if self.switch_intelligence.should_switch(context):
                best_switch: Optional[BattleMon] = self.switch_intelligence.find_best_switch(context)
                if best_switch is not None:
                    return SwitchAction(
                        position=battle_state.battle_position,
                        switch_in_pokemon_index=battle_state.team_party.index(best_switch),
                    )
        
        # Score available moves and pick best
        return self._evaluate_and_choose_move(context, battle_state)
    
    def _evaluate_endgame_action(
        self,
        context: AIContext,
    ) -> Optional[BattleAction]:
        """
        Evaluate endgame scenario and return optimized action.
        
        Args:
            context: AI battle context
            
        Returns:
            BattleAction if endgame strategy applies, None otherwise
        """
        from shared.battle.battle_actions import MoveAction
        
        active_mon: BattleMon = context.active_mon
        
        # Get endgame analysis
        endgame_info: dict = self.endgame_scenarios.evaluate_final_pokemon_scenario(context)
        
        # Check for 1v1 situations
        if not endgame_info.get("should_prioritize_survival", False):
            # Look for high-damage finishing move
            available_moves: List[Move] = list(active_mon.move_set.moves.values()) if hasattr(active_mon, "move_set") else []
            
            best_move: Optional[Move] = None
            best_score: float = -999.0
            
            for move in available_moves:
                if move.current_pp > 0:
                    score: float = self.endgame_scenarios.score_endgame_move(context, move)
                    if score > best_score:
                        best_score = score
                        best_move = move
            
            if best_move is not None:
                return MoveAction(
                    position=context.position,
                    move_index=best_move.index,
                    target_position=context.opponent_position,
                )
        else:
            # Survival priority - use healing or defensive move
            available_moves: List[Move] = list(active_mon.move_set.moves.values())
            
            # Find healing move first
            for move in available_moves:
                if move.current_pp > 0 and move.has_tag(HealMove):
                    return MoveAction(
                        position=context.position,
                        move_index=move.index,
                        target_position=context.opponent_position,
                    )
            
            # Find defensive/screen move
            for move in available_moves:
                if move.current_pp > 0 and move.has_tag(ScreenMove):
                    return MoveAction(
                        position=context.position,
                        move_index=move.index,
                        target_position=context.opponent_position,
                    )
        
        return None
    
    def _evaluate_setup_threat(
        self,
        context: AIContext,
    ) -> Optional["BattleAction"]:
        """
        Evaluate opponent setup threat and respond accordingly.
        
        Args:
            context: AI battle context
            
        Returns:
            BattleAction if setup threat should be handled, None otherwise
        """
        from shared.battle.battle_actions import MoveAction
        
        opponent: BattleMon = context.opponent_mon

        
        # Detect setup threat
        is_setup_threat, boost_stages = self.setup_recognition.detect_setup_threat(opponent)
        
        if not is_setup_threat:
            return None
        
        # Get sweep potential
        sweep_potential: float = self.setup_recognition.predict_sweep_potential(context, opponent)
        
        # High sweep potential (>0.7) - prioritize disruption
        if sweep_potential > 0.7:
            active_mon: BattleMon = context.active_mon
            available_moves: List[Move] = list(active_mon.move_set.moves.values())
            
            # Prioritize stat-lowering moves
            for move in available_moves:
                if move.current_pp > 0 and move.has_tag(StatChangeMove):
                    # Check if it lowers opponent stats
                    stat_tag: StatChangeMove = move.get_tag(StatChangeMove)  # type: ignore
                    if stat_tag and hasattr(stat_tag, "inflicted") and stat_tag.inflicted:
                        return MoveAction(
                            position=context.position,
                            move_index=move.index,
                            target_position=context.opponent_position,
                        )
        
        return None
    
    def _evaluate_and_choose_move(
        self,
        context: AIContext,
        battle_state: AIBattleState,
    ) -> "BattleAction":
        """
        Score all available moves and choose the best one.
        
        Args:
            context: AI battle context
            battle_state: AIBattleState for position info
            
        Returns:
            MoveAction for best move
        """
        from shared.battle.battle_actions import MoveAction
        
        active_mon: BattleMon = context.active_mon

        available_moves: List[Move] = list(active_mon.move_set.moves.values())
        
        best_move: Optional[Move] = None
        best_score: float = -999.0
        
        for move in available_moves:
            if move.current_pp <= 0:
                continue
            
            # Score the move
            base_score: float = self.move_scorer.score_move(
                move.base_move, active_mon, context.opponent_mon, context
            )
            
            # Apply personality modifiers
            adjusted_score: float = self.personality.apply_personality_to_move_score(
                base_score, move.base_move, active_mon
            )
            
            if adjusted_score > best_score:
                best_score = adjusted_score
                best_move = move
        
        if best_move is None:
            raise RuntimeError("No valid moves available")
        
        return MoveAction(
            position=battle_state.battle_position,
            move_index=best_move.index,
            target_position=battle_state.opponent_position,
        )
    
    def record_move_used(
        self,
        battler_id: UUID,
        move_name: str,
    ) -> None:
        """
        Record a move used (for opponent move memory).
        
        Args:
            battler_id: ID of battler using move
            move_name: Name of the move used
        """
        self.move_memory.record_move_used(battler_id, move_name)
    
    def record_switch(
        self,
        battler_id: UUID,
        pokemon_id: str,
    ) -> None:
        """
        Record a switch (for prediction system).
        
        Args:
            battler_id: ID of battler switching
            pokemon_id: ID/name of Pokemon switched to
        """
        self.prediction_system.record_switch(battler_id, pokemon_id)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled based on skill level.
        
        Args:
            feature: Feature name from FEATURE_GATES
            
        Returns:
            True if feature enabled, False otherwise
        """
        required_level: int = FEATURE_GATES.get(feature, 100)
        return self.skill_level >= required_level
    
    def get_threat_assessment(self, context: AIContext) -> Tuple[float, str]:
        """
        Get threat assessment for current battle state.
        
        Args:
            context: AI battle context
            
        Returns:
            Tuple of (threat_level, threat_description)
        """
        threat_level: float = self.threat_assessment.calculate_threat(context)
        
        # Describe threat
        if threat_level >= 8.0:
            description: str = "Critical threat"
        elif threat_level >= 6.0:
            description: str = "High threat"
        elif threat_level >= 4.0:
            description: str = "Moderate threat"
        elif threat_level >= 2.0:
            description: str = "Low threat"
        else:
            description: str = "Minimal threat"
        
        return threat_level, description
    
    def get_ai_status(self) -> dict[str, int | str | dict[str, bool]]:
        """
        Get current AI status and enabled features.
        
        Returns:
            Status dictionary
        """
        return {
            "skill_level": self.skill_level,
            "personality": self.personality.get_personality_name(),
            "battler_id": str(self.battler_id),
            "features_enabled": {
                name: self.is_feature_enabled(name)
                for name in FEATURE_GATES.keys()
            },
        }
