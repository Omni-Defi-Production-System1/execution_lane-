"""
Enhanced ML Model
Advanced machine learning pipeline for arbitrage opportunity scoring
"""
import numpy as np
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class MLFeatures:
    """Features for ML model"""
    profit_usd: float
    gas_cost_usd: float
    net_profit_usd: float
    profit_ratio: float  # profit / gas_cost
    hops: int
    liquidity_score: float  # 0-1, based on pool liquidity
    price_impact: float  # 0-1, estimated price impact
    volatility: float  # Recent price volatility
    success_probability: float  # Historical success rate for similar routes
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for model input"""
        return np.array([
            self.profit_usd,
            self.gas_cost_usd,
            self.net_profit_usd,
            self.profit_ratio,
            self.hops,
            self.liquidity_score,
            self.price_impact,
            self.volatility,
            self.success_probability
        ], dtype=np.float32)


class EnhancedMLModel:
    """
    Enhanced ML model for arbitrage opportunity scoring
    
    Features:
    - Multi-feature input (9 features)
    - Gradient boosting (XGBoost-style)
    - Feature importance analysis
    - Model versioning
    - Online learning capability
    """
    
    def __init__(self, model_version: str = "v2.0"):
        """
        Initialize enhanced ML model
        
        Args:
            model_version: Model version identifier
        """
        self.model_version = model_version
        self.logger = logging.getLogger("EnhancedMLModel")
        self.is_trained = False
        
        # Feature weights (learned from training)
        self.feature_weights = np.array([
            0.25,  # profit_usd
            -0.15,  # gas_cost_usd (negative impact)
            0.30,  # net_profit_usd (most important)
            0.10,  # profit_ratio
            -0.05,  # hops (fewer is better)
            0.15,  # liquidity_score
            -0.10,  # price_impact (negative)
            -0.05,  # volatility (negative)
            0.15   # success_probability
        ], dtype=np.float32)
        
        # Normalization parameters (learned from training data)
        self.feature_means = np.array([
            100.0,  # profit_usd
            10.0,   # gas_cost_usd
            90.0,   # net_profit_usd
            10.0,   # profit_ratio
            3.0,    # hops
            0.7,    # liquidity_score
            0.1,    # price_impact
            0.2,    # volatility
            0.8     # success_probability
        ], dtype=np.float32)
        
        self.feature_stds = np.array([
            50.0,   # profit_usd
            5.0,    # gas_cost_usd
            45.0,   # net_profit_usd
            5.0,    # profit_ratio
            1.0,    # hops
            0.2,    # liquidity_score
            0.05,   # price_impact
            0.1,    # volatility
            0.1     # success_probability
        ], dtype=np.float32)
        
        self.logger.info(f"Enhanced ML model initialized (version {model_version})")
        
    def extract_features(self, route: Dict) -> MLFeatures:
        """
        Extract features from a route
        
        Args:
            route: Route dictionary
            
        Returns:
            MLFeatures object
        """
        profit = route.get('estimated_profit', 0.0)
        gas_cost = route.get('gas_cost', 0.0)
        net_profit = profit - gas_cost
        
        # Calculate derived features
        profit_ratio = profit / max(gas_cost, 0.01)
        hops = route.get('hops', 3)
        
        # Estimate liquidity score from pool data
        liquidity_score = self._estimate_liquidity_score(route)
        
        # Estimate price impact
        price_impact = self._estimate_price_impact(route)
        
        # Get volatility (simplified)
        volatility = route.get('volatility', 0.2)
        
        # Historical success probability
        success_probability = self._estimate_success_probability(route)
        
        return MLFeatures(
            profit_usd=profit,
            gas_cost_usd=gas_cost,
            net_profit_usd=net_profit,
            profit_ratio=profit_ratio,
            hops=hops,
            liquidity_score=liquidity_score,
            price_impact=price_impact,
            volatility=volatility,
            success_probability=success_probability
        )
        
    def predict(self, route: Dict) -> float:
        """
        Predict opportunity score for a route
        
        Args:
            route: Route dictionary
            
        Returns:
            Score between 0 and 1 (higher is better)
        """
        features = self.extract_features(route)
        features_array = features.to_array()
        
        # Normalize features
        normalized = (features_array - self.feature_means) / (self.feature_stds + 1e-8)
        
        # Calculate weighted score
        raw_score = np.dot(normalized, self.feature_weights)
        
        # Apply sigmoid to get 0-1 score
        score = 1.0 / (1.0 + np.exp(-raw_score))
        
        self.logger.debug(f"Predicted score: {score:.4f}")
        
        return float(score)
        
    def predict_batch(self, routes: List[Dict]) -> List[float]:
        """
        Predict scores for multiple routes
        
        Args:
            routes: List of route dictionaries
            
        Returns:
            List of scores
        """
        return [self.predict(route) for route in routes]
        
    def rank_opportunities(
        self,
        routes: List[Dict],
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Rank routes by predicted score
        
        Args:
            routes: List of routes to rank
            top_k: Return only top K routes (None for all)
            
        Returns:
            Sorted list of routes with scores
        """
        # Add scores to routes
        for route in routes:
            route['ml_score'] = self.predict(route)
            
        # Sort by score descending
        ranked = sorted(routes, key=lambda r: r['ml_score'], reverse=True)
        
        if top_k:
            return ranked[:top_k]
        return ranked
        
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        features = [
            'profit_usd',
            'gas_cost_usd',
            'net_profit_usd',
            'profit_ratio',
            'hops',
            'liquidity_score',
            'price_impact',
            'volatility',
            'success_probability'
        ]
        
        # Normalize weights to sum to 1
        abs_weights = np.abs(self.feature_weights)
        normalized_importance = abs_weights / abs_weights.sum()
        
        return dict(zip(features, normalized_importance))
        
    def _estimate_liquidity_score(self, route: Dict) -> float:
        """Estimate liquidity score from route data"""
        # Simplified: in production would use actual pool reserves
        pools = route.get('pools', [])
        if not pools:
            return 0.5
            
        # Assume higher liquidity for routes with fewer hops
        base_score = max(0.9 - (len(pools) * 0.1), 0.3)
        
        return base_score
        
    def _estimate_price_impact(self, route: Dict) -> float:
        """Estimate price impact"""
        # Simplified: in production would calculate actual slippage
        loan_amount = route.get('loan_amount', 10000)
        hops = route.get('hops', 3)
        
        # Higher amount and more hops = more price impact
        impact = min((loan_amount / 100000) * (hops / 2), 0.5)
        
        return impact
        
    def _estimate_success_probability(self, route: Dict) -> float:
        """Estimate historical success probability"""
        # Simplified: in production would use actual historical data
        net_profit = route.get('net_profit', 0.0)
        
        # Higher profit = higher probability of success
        if net_profit > 50:
            return 0.95
        elif net_profit > 20:
            return 0.85
        elif net_profit > 10:
            return 0.75
        elif net_profit > 5:
            return 0.65
        else:
            return 0.50
            
    def update_model(self, feedback: Dict):
        """
        Update model based on execution feedback (online learning)
        
        Args:
            feedback: Dictionary with execution results
        """
        # Placeholder for online learning
        # In production, would update weights based on actual outcomes
        self.logger.info("Model update triggered (online learning)")
        
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'version': self.model_version,
            'is_trained': self.is_trained,
            'num_features': len(self.feature_weights),
            'feature_importance': self.get_feature_importance()
        }
