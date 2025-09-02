"""
Multi-Agent Marketing System - Data Processing Utilities
Utility classes for data processing, ML pipeline, and memory management
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Data processing utility class for handling marketing data
    """
    
    def __init__(self, data_path: str = "./data/"):
        self.data_path = data_path
        self.scalers = {}
        self.encoders = {}
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load data from CSV files"""
        try:
            # For demo purposes, create sample data if files don't exist
            sample_data = self._create_sample_data()
            logger.info("Loaded sample data for demonstration")
            return sample_data
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return {}
    
    def clean_data(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Clean and preprocess data"""
        cleaned_data = {}
        
        for name, df in dataframes.items():
            try:
                # Remove duplicates
                df_clean = df.drop_duplicates()
                
                # Handle missing values
                df_clean = df_clean.fillna(method='ffill')
                
                cleaned_data[name] = df_clean
                logger.info(f"Cleaned {name}: {df_clean.shape[0]} rows")
                
            except Exception as e:
                logger.error(f"Error cleaning {name}: {str(e)}")
                cleaned_data[name] = df
                
        return cleaned_data
    
    def engineer_features(self, dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Engineer features for ML models"""
        try:
            # Combine relevant data for feature engineering
            if 'leads' in dataframes:
                leads_df = dataframes['leads']
                
                # Create features
                features = pd.DataFrame()
                
                # Company size encoding
                size_mapping = {
                    '1-10': 1, '11-50': 2, '51-200': 3,
                    '201-1000': 4, '1001-5000': 5, '5000+': 6
                }
                features['company_size_encoded'] = leads_df['company_size'].map(size_mapping)
                
                # Industry encoding
                features['is_saas'] = (leads_df['industry'] == 'SaaS').astype(int)
                features['is_fintech'] = (leads_df['industry'] == 'FinTech').astype(int)
                features['is_healthtech'] = (leads_df['industry'] == 'HealthTech').astype(int)
                
                # Persona encoding
                features['is_decision_maker'] = leads_df['persona'].isin(['Founder', 'CMO', 'CTO']).astype(int)
                
                # Region encoding
                features['is_priority_region'] = leads_df['region'].isin(['US', 'EU']).astype(int)
                
                # Source encoding
                features['is_high_intent'] = leads_df['source'].isin(['Website', 'Referral']).astype(int)
                
                # Add original data
                for col in leads_df.columns:
                    if col not in features.columns:
                        features[col] = leads_df[col]
                
                return features
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            return pd.DataFrame()
    
    def _create_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Create sample data for demonstration"""
        sample_data = {}
        
        # Sample leads data
        leads_data = {
            'lead_id': [f'L{i:03d}' for i in range(1, 101)],
            'company_name': [f'Company {i}' for i in range(1, 101)],
            'industry': np.random.choice(['SaaS', 'FinTech', 'HealthTech', 'E-commerce', 'Manufacturing'], 100),
            'company_size': np.random.choice(['1-10', '11-50', '51-200', '201-1000', '1001-5000', '5000+'], 100),
            'persona': np.random.choice(['Founder', 'CMO', 'CTO', 'Marketing Manager', 'Sales Manager'], 100),
            'region': np.random.choice(['US', 'EU', 'APAC', 'LATAM'], 100),
            'source': np.random.choice(['Website', 'Google Ads', 'LinkedIn', 'Referral', 'Cold Outreach'], 100),
            'created_at': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(100)]
        }
        sample_data['leads'] = pd.DataFrame(leads_data)
        
        # Sample campaign data
        campaign_data = {
            'campaign_id': [f'C{i:03d}' for i in range(1, 21)],
            'campaign_name': [f'Campaign {i}' for i in range(1, 21)],
            'ctr': np.random.uniform(0.01, 0.05, 20),
            'cpl_usd': np.random.uniform(20, 100, 20),
            'roas': np.random.uniform(0.5, 3.0, 20),
            'conversions': np.random.randint(0, 50, 20),
            'cost_usd': np.random.uniform(100, 5000, 20),
            'daily_budget_usd': np.random.uniform(50, 200, 20)
        }
        sample_data['campaigns'] = pd.DataFrame(campaign_data)
        
        return sample_data

class MLPipeline:
    """
    Machine learning pipeline utility class
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
    def prepare_training_data(self, feature_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for ML models"""
        try:
            if feature_data.empty:
                return np.array([]), np.array([])
            
            # Select features for training
            feature_columns = [
                'company_size_encoded', 'is_saas', 'is_fintech', 'is_healthtech',
                'is_decision_maker', 'is_priority_region', 'is_high_intent'
            ]
            
            # Filter available features
            available_features = [col for col in feature_columns if col in feature_data.columns]
            
            if not available_features:
                return np.array([]), np.array([])
            
            X = feature_data[available_features].values
            
            # Create synthetic target variable for demonstration
            # In production, this would be actual conversion data
            y = np.random.choice([0, 1], size=len(X), p=[0.7, 0.3])
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return np.array([]), np.array([])
    
    def train_ensemble_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train ensemble ML models"""
        try:
            if len(X) == 0 or len(y) == 0:
                logger.warning("No training data available")
                return {}
            
            trained_models = {}
            
            # Random Forest
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X, y)
            trained_models['random_forest'] = rf_model
            
            # Gradient Boosting
            gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            gb_model.fit(X, y)
            trained_models['gradient_boosting'] = gb_model
            
            # Logistic Regression
            lr_model = LogisticRegression(random_state=42)
            lr_model.fit(X, y)
            trained_models['logistic_regression'] = lr_model
            
            logger.info(f"Trained {len(trained_models)} models")
            return trained_models
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            return {}
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """Make predictions using trained model"""
        try:
            if model_name not in self.models:
                logger.error(f"Model {model_name} not found")
                return np.array([])
            
            return self.models[model_name].predict(X)
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return np.array([])

class AgentMemorySystem:
    """
    Memory system utility class for agents
    """
    
    def __init__(self):
        self.short_term_memory = {}
        self.long_term_memory = {}
        self.episodic_memory = []
        self.semantic_knowledge = []
        
    def store_short_term(self, conversation_id: str, context: Dict[str, Any], ttl_hours: int = 24):
        """Store short-term memory for conversation context"""
        try:
            self.short_term_memory[conversation_id] = {
                'context': context,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=ttl_hours)
            }
            logger.info(f"Stored short-term memory for conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error storing short-term memory: {str(e)}")
    
    def retrieve_short_term(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve short-term memory for conversation"""
        try:
            if conversation_id in self.short_term_memory:
                memory = self.short_term_memory[conversation_id]
                
                # Check if expired
                if datetime.now() > memory['expires_at']:
                    del self.short_term_memory[conversation_id]
                    return None
                
                return memory['context']
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving short-term memory: {str(e)}")
            return None
    
    def update_long_term(self, lead_id: str, preferences: Dict[str, Any], rfm_score: float):
        """Update long-term memory for lead preferences"""
        try:
            self.long_term_memory[lead_id] = {
                'preferences': preferences,
                'rfm_score': rfm_score,
                'updated_at': datetime.now()
            }
            logger.info(f"Updated long-term memory for lead {lead_id}")
        except Exception as e:
            logger.error(f"Error updating long-term memory: {str(e)}")
    
    def store_episode(self, scenario: str, actions: List[Dict[str, Any]], 
                     outcome_score: float, notes: str = ""):
        """Store episodic memory for learning"""
        try:
            episode = {
                'scenario': scenario,
                'actions': actions,
                'outcome_score': outcome_score,
                'notes': notes,
                'timestamp': datetime.now()
            }
            self.episodic_memory.append(episode)
            logger.info(f"Stored episodic memory for scenario: {scenario}")
        except Exception as e:
            logger.error(f"Error storing episodic memory: {str(e)}")
    
    def retrieve_similar_episodes(self, scenario: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar episodes for learning"""
        try:
            # Simple similarity based on scenario text
            similar_episodes = []
            
            for episode in self.episodic_memory:
                if scenario.lower() in episode['scenario'].lower():
                    similar_episodes.append(episode)
            
            # Sort by outcome score and return top_k
            similar_episodes.sort(key=lambda x: x['outcome_score'], reverse=True)
            return similar_episodes[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving similar episodes: {str(e)}")
            return []
    
    def update_semantic_knowledge(self, subject: str, predicate: str, object_val: str, weight: float = 1.0):
        """Update semantic knowledge graph"""
        try:
            triple = {
                'subject': subject,
                'predicate': predicate,
                'object': object_val,
                'weight': weight,
                'timestamp': datetime.now()
            }
            self.semantic_knowledge.append(triple)
            logger.info(f"Updated semantic knowledge: {subject} {predicate} {object_val}")
        except Exception as e:
            logger.error(f"Error updating semantic knowledge: {str(e)}")
    
    def query_semantic_knowledge(self, subject: str = None, predicate: str = None, 
                               object_val: str = None) -> List[Dict[str, Any]]:
        """Query semantic knowledge graph"""
        try:
            results = []
            
            for triple in self.semantic_knowledge:
                match = True
                
                if subject and triple['subject'] != subject:
                    match = False
                if predicate and triple['predicate'] != predicate:
                    match = False
                if object_val and triple['object'] != object_val:
                    match = False
                
                if match:
                    results.append(triple)
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying semantic knowledge: {str(e)}")
            return []
