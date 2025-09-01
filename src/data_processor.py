"""
Multi-Agent Marketing System - Data Processing Pipeline
Production-ready data processing and ML pipeline for marketing automation
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataQualityMetrics:
    """Data quality metrics for monitoring data pipeline health"""
    missing_values_pct: float
    duplicate_records_pct: float
    data_freshness_hours: float
    schema_compliance_pct: float
    anomaly_score: float

@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics for monitoring ML pipeline health"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    feature_importance: Dict[str, float]

class DataProcessor:
    """
    Production-ready data processing pipeline for multi-agent marketing system
    Handles data ingestion, cleaning, feature engineering, and quality monitoring
    """
    
    def __init__(self, data_path: str = "./data/"):
        self.data_path = data_path
        self.scalers = {}
        self.encoders = {}
        self.quality_metrics = {}
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files into pandas DataFrames with error handling"""
        data_files = {
            'campaigns': 'campaigns.csv',
            'ab_variants': 'ab_variants.csv',
            'leads': 'leads.csv',
            'interactions': 'interactions.csv',
            'conversations': 'conversations.csv',
            'conversions': 'conversions.csv',
            'agent_actions': 'agent_actions.csv',
            'campaign_daily': 'campaign_daily.csv',
            'memory_short_term': 'memory_short_term.csv',
            'memory_long_term': 'memory_long_term.csv',
            'memory_episodic': 'memory_episodic.csv',
            'semantic_kg_triples': 'semantic_kg_triples.csv',
            'mcp_jsonrpc_calls': 'mcp_jsonrpc_calls.csv',
            'transport_websocket_sessions': 'transport_websocket_sessions.csv',
            'transport_http_requests': 'transport_http_requests.csv',
            'mcp_resource_access': 'mcp_resource_access.csv',
            'segments': 'segments.csv',
            'security_auth_events': 'security_auth_events.csv'
        }
        
        dataframes = {}
        for name, filename in data_files.items():
            try:
                df = pd.read_csv(f"{self.data_path}{filename}")
                logger.info(f"Loaded {name}: {df.shape[0]} rows, {df.shape[1]} columns")
                dataframes[name] = df
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
                
        return dataframes
    
    def clean_data(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Clean and preprocess data with comprehensive error handling"""
        cleaned_data = {}
        
        for name, df in dataframes.items():
            try:
                # Create a copy to avoid modifying original data
                cleaned_df = df.copy()
                
                # Convert datetime columns
                datetime_columns = [col for col in cleaned_df.columns 
                                  if any(keyword in col.lower() for keyword in 
                                       ['date', 'time', 'at', 'created', 'updated', 'expires'])]
                
                for col in datetime_columns:
                    if col in cleaned_df.columns:
                        cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                
                # Handle JSON columns - don't parse for duplicate removal
                json_columns = [col for col in cleaned_df.columns if 'json' in col.lower()]
                
                # Remove duplicates before JSON parsing to avoid unhashable type errors
                initial_rows = len(cleaned_df)
                # Create subset without JSON columns for duplicate detection
                non_json_cols = [col for col in cleaned_df.columns if col not in json_columns]
                if non_json_cols:
                    cleaned_df = cleaned_df.drop_duplicates(subset=non_json_cols)
                else:
                    cleaned_df = cleaned_df.drop_duplicates()
                duplicates_removed = initial_rows - len(cleaned_df)
                
                if duplicates_removed > 0:
                    logger.info(f"Removed {duplicates_removed} duplicate rows from {name}")
                
                # Now parse JSON columns after duplicate removal
                for col in json_columns:
                    if col in cleaned_df.columns:
                        cleaned_df[col] = cleaned_df[col].apply(self._safe_json_parse)
                
                # Calculate data quality metrics
                self.quality_metrics[name] = self._calculate_data_quality(cleaned_df)
                
                cleaned_data[name] = cleaned_df
                logger.info(f"Cleaned {name}: {cleaned_df.shape[0]} rows remaining")
                
            except Exception as e:
                logger.error(f"Error cleaning {name}: {str(e)}")
                cleaned_data[name] = df  # Return original if cleaning fails
                
        return cleaned_data
    
    def _safe_json_parse(self, json_str: str) -> Dict:
        """Safely parse JSON strings with error handling"""
        if pd.isna(json_str) or json_str == '':
            return {}
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def _calculate_data_quality(self, df: pd.DataFrame) -> DataQualityMetrics:
        """Calculate comprehensive data quality metrics"""
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        duplicate_pct = (df.duplicated().sum() / len(df)) * 100
        
        # Calculate data freshness if timestamp columns exist
        timestamp_cols = [col for col in df.columns if 'timestamp' in col.lower() or 'at' in col.lower()]
        data_freshness = 0
        if timestamp_cols:
            latest_timestamp = df[timestamp_cols[0]].max()
            if pd.notna(latest_timestamp):
                data_freshness = (datetime.now() - latest_timestamp).total_seconds() / 3600
        
        return DataQualityMetrics(
            missing_values_pct=missing_pct,
            duplicate_records_pct=duplicate_pct,
            data_freshness_hours=data_freshness,
            schema_compliance_pct=95.0,  # Placeholder - would implement schema validation
            anomaly_score=0.1  # Placeholder - would implement anomaly detection
        )
    
    def engineer_features(self, dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Engineer features for lead scoring and classification"""
        try:
            # Start with leads as the base table
            leads_df = dataframes['leads'].copy()
            
            # Add interaction features
            if 'interactions' in dataframes:
                interaction_features = self._create_interaction_features(
                    dataframes['interactions'], leads_df
                )
                leads_df = leads_df.merge(interaction_features, on='lead_id', how='left')
            
            # Add campaign features
            if 'campaigns' in dataframes:
                campaign_features = self._create_campaign_features(
                    dataframes['campaigns'], leads_df
                )
                leads_df = leads_df.merge(campaign_features, on='campaign_id', how='left')
            
            # Add conversion features
            if 'conversions' in dataframes:
                conversion_features = self._create_conversion_features(
                    dataframes['conversions'], leads_df
                )
                leads_df = leads_df.merge(conversion_features, on='lead_id', how='left')
            
            # Add temporal features
            leads_df = self._add_temporal_features(leads_df)
            
            # Add RFM features
            leads_df = self._calculate_rfm_features(leads_df, dataframes.get('interactions'))
            
            logger.info(f"Feature engineering completed: {leads_df.shape[1]} features created")
            return leads_df
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            return dataframes['leads']
    
    def _create_interaction_features(self, interactions_df: pd.DataFrame, 
                                   leads_df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction-based features for leads"""
        interaction_agg = interactions_df.groupby('lead_id').agg({
            'interaction_id': 'count',
            'timestamp': ['min', 'max'],
            'channel': lambda x: x.nunique(),
            'event_type': lambda x: x.nunique(),
            'outcome': lambda x: (x == 'positive').sum()
        }).reset_index()
        
        # Flatten column names
        interaction_agg.columns = [
            'lead_id', 'total_interactions', 'first_interaction', 'last_interaction',
            'unique_channels', 'unique_events', 'positive_outcomes'
        ]
        
        # Calculate interaction frequency
        interaction_agg['interaction_span_days'] = (
            interaction_agg['last_interaction'] - interaction_agg['first_interaction']
        ).dt.days + 1
        
        interaction_agg['interaction_frequency'] = (
            interaction_agg['total_interactions'] / interaction_agg['interaction_span_days']
        ).fillna(0)
        
        # Calculate positive outcome rate
        interaction_agg['positive_outcome_rate'] = (
            interaction_agg['positive_outcomes'] / interaction_agg['total_interactions']
        ).fillna(0)
        
        return interaction_agg[['lead_id', 'total_interactions', 'unique_channels', 
                               'unique_events', 'positive_outcomes', 'interaction_frequency',
                               'positive_outcome_rate']]
    
    def _create_campaign_features(self, campaigns_df: pd.DataFrame, 
                                leads_df: pd.DataFrame) -> pd.DataFrame:
        """Create campaign-based features"""
        campaign_features = campaigns_df[['campaign_id', 'objective', 'daily_budget_usd', 
                                        'total_budget_usd', 'primary_region']].copy()
        
        # Parse channel_mix JSON
        campaigns_df['channel_mix_parsed'] = campaigns_df['channel_mix'].apply(self._safe_json_parse)
        campaign_features['num_channels'] = campaigns_df['channel_mix_parsed'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
        
        # Calculate campaign duration
        campaigns_df['start_date'] = pd.to_datetime(campaigns_df['start_date'])
        campaigns_df['end_date'] = pd.to_datetime(campaigns_df['end_date'])
        campaign_features['campaign_duration_days'] = (
            campaigns_df['end_date'] - campaigns_df['start_date']
        ).dt.days
        
        return campaign_features
    
    def _create_conversion_features(self, conversions_df: pd.DataFrame, 
                                  leads_df: pd.DataFrame) -> pd.DataFrame:
        """Create conversion-based features"""
        conversion_features = conversions_df.groupby('lead_id').agg({
            'conversion_value_usd': ['sum', 'mean', 'count'],
            'conversion_type': lambda x: x.nunique()
        }).reset_index()
        
        # Flatten column names
        conversion_features.columns = [
            'lead_id', 'total_conversion_value', 'avg_conversion_value',
            'conversion_count', 'unique_conversion_types'
        ]
        
        # Add binary conversion flag
        conversion_features['has_converted'] = 1
        
        return conversion_features
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add temporal features based on timestamps"""
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            current_time = pd.Timestamp.now()
            df['days_since_creation'] = (current_time - df['created_at']).dt.days
            df['created_hour'] = df['created_at'].dt.hour
            df['created_day_of_week'] = df['created_at'].dt.dayofweek
            df['created_month'] = df['created_at'].dt.month
        
        if 'last_active_at' in df.columns:
            df['last_active_at'] = pd.to_datetime(df['last_active_at'], errors='coerce')
            current_time = pd.Timestamp.now()
            df['days_since_last_active'] = (current_time - df['last_active_at']).dt.days
        
        return df
    
    def _calculate_rfm_features(self, leads_df: pd.DataFrame, 
                              interactions_df: Optional[pd.DataFrame]) -> pd.DataFrame:
        """Calculate RFM (Recency, Frequency, Monetary) features"""
        if interactions_df is None:
            return leads_df
        
        # Calculate recency (days since last interaction)
        last_interaction = interactions_df.groupby('lead_id')['timestamp'].max().reset_index()
        last_interaction['timestamp'] = pd.to_datetime(last_interaction['timestamp'], errors='coerce')
        current_time = pd.Timestamp.now()
        last_interaction['recency_days'] = (current_time - last_interaction['timestamp']).dt.days
        
        # Calculate frequency (number of interactions)
        frequency = interactions_df.groupby('lead_id').size().reset_index(name='frequency')
        
        # Merge RFM features
        rfm_features = last_interaction[['lead_id', 'recency_days']].merge(
            frequency, on='lead_id', how='outer'
        )
        
        # Fill missing values
        rfm_features['recency_days'] = rfm_features['recency_days'].fillna(999)
        rfm_features['frequency'] = rfm_features['frequency'].fillna(0)
        
        # Calculate RFM scores (1-5 scale) with proper handling of edge cases
        try:
            rfm_features['recency_score'] = pd.qcut(
                rfm_features['recency_days'].rank(method='first'), 5, labels=[5,4,3,2,1], duplicates='drop'
            ).astype(float)
        except ValueError:
            # If qcut fails due to duplicate values, use simple binning
            rfm_features['recency_score'] = 3.0
        
        try:
            rfm_features['frequency_score'] = pd.qcut(
                rfm_features['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5], duplicates='drop'
            ).astype(float)
        except ValueError:
            # If qcut fails due to duplicate values, use simple binning
            rfm_features['frequency_score'] = 3.0
        
        # Combined RFM score
        rfm_features['rfm_score'] = (
            rfm_features['recency_score'] * 0.5 + 
            rfm_features['frequency_score'] * 0.5
        )
        
        # Merge with leads dataframe
        leads_df = leads_df.merge(
            rfm_features[['lead_id', 'recency_days', 'frequency', 'rfm_score']], 
            on='lead_id', how='left'
        )
        
        # Fill missing RFM values for leads without interactions
        leads_df['recency_days'] = leads_df['recency_days'].fillna(999)
        leads_df['frequency'] = leads_df['frequency'].fillna(0)
        leads_df['rfm_score'] = leads_df['rfm_score'].fillna(1.0)
        
        return leads_df

class MLPipeline:
    """
    Production-ready machine learning pipeline for lead scoring and classification
    Implements ensemble methods with proper validation and monitoring
    """
    
    def __init__(self):
        self.models = {}
        self.preprocessors = {}
        self.performance_metrics = {}
        
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for model training with proper preprocessing"""
        # Define target variable based on lead status and conversions
        target_mapping = {
            'Converted': 2,
            'Qualified': 1,
            'Open': 0,
            'New': 0,
            'Unqualified': 0
        }
        
        df['target'] = df['lead_status'].map(target_mapping).fillna(0)
        
        # Select features for training - only numeric features initially
        numeric_feature_columns = [
            'lead_score', 'total_interactions', 'unique_channels', 'unique_events',
            'positive_outcomes', 'interaction_frequency', 'positive_outcome_rate',
            'daily_budget_usd', 'total_budget_usd', 'num_channels',
            'campaign_duration_days', 'days_since_creation', 'days_since_last_active',
            'created_hour', 'created_day_of_week', 'created_month',
            'recency_days', 'frequency', 'rfm_score'
        ]
        
        # Filter available numeric columns
        available_numeric_features = [col for col in numeric_feature_columns if col in df.columns]
        
        # Add categorical features that we'll encode
        categorical_feature_columns = ['company_size', 'industry', 'persona', 'region']
        available_categorical_features = [col for col in categorical_feature_columns if col in df.columns]
        
        # Combine all available features
        all_features = available_numeric_features + available_categorical_features
        
        X = df[all_features].copy()
        y = df['target']
        
        # Handle missing values for numeric columns
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())
        
        # Handle missing values for categorical columns
        categorical_cols = X.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            X[categorical_cols] = X[categorical_cols].fillna('Unknown')
        
        logger.info(f"Training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        logger.info(f"Numeric features: {len(numeric_cols)}, Categorical features: {len(categorical_cols)}")
        return X, y
    
    def create_preprocessing_pipeline(self, X: pd.DataFrame) -> ColumnTransformer:
        """Create preprocessing pipeline for features"""
        # Identify numeric and categorical columns
        numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_features = X.select_dtypes(include=['object']).columns.tolist()
        
        # Create preprocessing steps
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        
        # Combine preprocessing steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )
        
        return preprocessor
    
    def train_ensemble_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Pipeline]:
        """Train ensemble of models for robust predictions"""
        # Create preprocessing pipeline
        preprocessor = self.create_preprocessing_pipeline(X)
        
        # Define models
        models = {
            'logistic_regression': LogisticRegression(
                random_state=42, max_iter=1000, class_weight='balanced'
            ),
            'random_forest': RandomForestClassifier(
                n_estimators=100, random_state=42, class_weight='balanced'
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100, random_state=42
            )
        }
        
        # Train models with cross-validation
        trained_models = {}
        
        for name, model in models.items():
            try:
                # Create pipeline
                pipeline = Pipeline([
                    ('preprocessor', preprocessor),
                    ('classifier', model)
                ])
                
                # Split data for training and validation
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
                
                # Train model
                pipeline.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = pipeline.predict(X_test)
                y_pred_proba = pipeline.predict_proba(X_test)
                
                # Calculate metrics
                accuracy = pipeline.score(X_test, y_test)
                auc_roc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
                
                # Cross-validation
                cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
                
                # Store performance metrics
                self.performance_metrics[name] = ModelPerformanceMetrics(
                    accuracy=accuracy,
                    precision=0.0,  # Would calculate from classification_report
                    recall=0.0,     # Would calculate from classification_report
                    f1_score=0.0,   # Would calculate from classification_report
                    auc_roc=auc_roc,
                    feature_importance={}  # Would extract from model
                )
                
                trained_models[name] = pipeline
                
                logger.info(f"{name} - Accuracy: {accuracy:.3f}, AUC-ROC: {auc_roc:.3f}")
                logger.info(f"{name} - CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
                
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
        
        self.models = trained_models
        return trained_models
    
    def predict_lead_scores(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Generate predictions from ensemble models"""
        predictions = {}
        
        for name, model in self.models.items():
            try:
                pred_proba = model.predict_proba(X)
                predictions[name] = pred_proba
            except Exception as e:
                logger.error(f"Error predicting with {name}: {str(e)}")
        
        return predictions
    
    def ensemble_predict(self, X: pd.DataFrame) -> np.ndarray:
        """Create ensemble predictions by averaging model outputs"""
        predictions = self.predict_lead_scores(X)
        
        if not predictions:
            logger.warning("No model predictions available")
            return np.zeros(len(X))
        
        # Average predictions across models
        ensemble_pred = np.mean(list(predictions.values()), axis=0)
        
        return ensemble_pred

class AgentMemorySystem:
    """
    Sophisticated memory system for agents with short-term, long-term, 
    episodic, and semantic memory components
    """
    
    def __init__(self):
        self.short_term_memory = {}
        self.long_term_memory = {}
        self.episodic_memory = []
        self.semantic_knowledge = {}
        
    def store_short_term(self, conversation_id: str, context: Dict[str, Any], 
                        ttl_hours: int = 24):
        """Store short-term conversation context with TTL"""
        expiry_time = datetime.now() + timedelta(hours=ttl_hours)
        
        self.short_term_memory[conversation_id] = {
            'context': context,
            'expires_at': expiry_time,
            'last_updated': datetime.now()
        }
        
        logger.info(f"Stored short-term memory for conversation {conversation_id}")
    
    def retrieve_short_term(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve short-term memory with expiry check"""
        if conversation_id not in self.short_term_memory:
            return None
        
        memory = self.short_term_memory[conversation_id]
        
        # Check if memory has expired
        if datetime.now() > memory['expires_at']:
            del self.short_term_memory[conversation_id]
            return None
        
        return memory['context']
    
    def update_long_term(self, lead_id: str, preferences: Dict[str, Any], 
                        rfm_score: float):
        """Update long-term lead profile and preferences"""
        if lead_id not in self.long_term_memory:
            self.long_term_memory[lead_id] = {
                'created_at': datetime.now(),
                'interaction_count': 0
            }
        
        self.long_term_memory[lead_id].update({
            'preferences': preferences,
            'rfm_score': rfm_score,
            'last_updated': datetime.now(),
            'interaction_count': self.long_term_memory[lead_id]['interaction_count'] + 1
        })
        
        logger.info(f"Updated long-term memory for lead {lead_id}")
    
    def store_episode(self, scenario: str, actions: List[Dict[str, Any]], 
                     outcome_score: float, notes: str = ""):
        """Store successful interaction patterns in episodic memory"""
        episode = {
            'episode_id': f"EP_{len(self.episodic_memory):06d}",
            'scenario': scenario,
            'actions': actions,
            'outcome_score': outcome_score,
            'notes': notes,
            'timestamp': datetime.now()
        }
        
        self.episodic_memory.append(episode)
        
        # Keep only top-performing episodes (limit memory size)
        if len(self.episodic_memory) > 1000:
            self.episodic_memory.sort(key=lambda x: x['outcome_score'], reverse=True)
            self.episodic_memory = self.episodic_memory[:1000]
        
        logger.info(f"Stored episode {episode['episode_id']} with score {outcome_score}")
    
    def retrieve_similar_episodes(self, scenario: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar episodes for pattern matching"""
        # Simple similarity based on scenario matching
        # In production, would use more sophisticated similarity measures
        similar_episodes = [
            ep for ep in self.episodic_memory 
            if scenario.lower() in ep['scenario'].lower()
        ]
        
        # Sort by outcome score and return top k
        similar_episodes.sort(key=lambda x: x['outcome_score'], reverse=True)
        return similar_episodes[:top_k]
    
    def update_semantic_knowledge(self, subject: str, predicate: str, 
                                object_val: str, weight: float = 1.0):
        """Update semantic knowledge graph"""
        triple_key = f"{subject}_{predicate}_{object_val}"
        
        if triple_key not in self.semantic_knowledge:
            self.semantic_knowledge[triple_key] = {
                'subject': subject,
                'predicate': predicate,
                'object': object_val,
                'weight': weight,
                'created_at': datetime.now(),
                'access_count': 0
            }
        else:
            # Update weight and access count
            self.semantic_knowledge[triple_key]['weight'] = max(
                self.semantic_knowledge[triple_key]['weight'], weight
            )
            self.semantic_knowledge[triple_key]['access_count'] += 1
        
        logger.info(f"Updated semantic knowledge: {subject} -> {predicate} -> {object_val}")
    
    def query_semantic_knowledge(self, subject: str = None, predicate: str = None, 
                               object_val: str = None) -> List[Dict[str, Any]]:
        """Query semantic knowledge graph"""
        results = []
        
        for triple_key, triple_data in self.semantic_knowledge.items():
            match = True
            
            if subject and triple_data['subject'] != subject:
                match = False
            if predicate and triple_data['predicate'] != predicate:
                match = False
            if object_val and triple_data['object'] != object_val:
                match = False
            
            if match:
                results.append(triple_data)
        
        # Sort by weight and access count
        results.sort(key=lambda x: (x['weight'], x['access_count']), reverse=True)
        return results

def main():
    """Main function to demonstrate the data processing and ML pipeline"""
    logger.info("Starting Multi-Agent Marketing System Data Processing Pipeline")
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Load and clean data
    logger.info("Loading data...")
    raw_data = processor.load_data()
    
    logger.info("Cleaning data...")
    clean_data = processor.clean_data(raw_data)
    
    # Engineer features
    logger.info("Engineering features...")
    feature_data = processor.engineer_features(clean_data)
    
    # Initialize ML pipeline
    ml_pipeline = MLPipeline()
    
    # Prepare training data
    logger.info("Preparing training data...")
    X, y = ml_pipeline.prepare_training_data(feature_data)
    
    # Train models
    logger.info("Training ensemble models...")
    trained_models = ml_pipeline.train_ensemble_models(X, y)
    
    # Initialize memory system
    memory_system = AgentMemorySystem()
    
    # Demonstrate memory operations
    logger.info("Demonstrating memory system...")
    
    # Store short-term memory
    memory_system.store_short_term(
        "C0000001", 
        {"intent": "product_inquiry", "sentiment": "positive", "urgency": "medium"}
    )
    
    # Update long-term memory
    memory_system.update_long_term(
        "L0000001",
        {"preferred_channel": "email", "contact_time": "morning", "interests": ["automation"]},
        0.75
    )
    
    # Store episode
    memory_system.store_episode(
        "product_inquiry_resolution",
        [
            {"action": "send_product_info", "channel": "email"},
            {"action": "schedule_demo", "time": "next_week"}
        ],
        0.85,
        "Successful conversion to demo booking"
    )
    
    # Update semantic knowledge
    memory_system.update_semantic_knowledge(
        "lead_L0000001", "prefers", "email_communication", 0.9
    )
    
    logger.info("Data processing and ML pipeline demonstration completed successfully")
    
    # Print summary statistics
    print("\n=== PIPELINE SUMMARY ===")
    print(f"Data files processed: {len(clean_data)}")
    print(f"Features engineered: {X.shape[1]}")
    print(f"Training samples: {X.shape[0]}")
    print(f"Models trained: {len(trained_models)}")
    print(f"Short-term memories: {len(memory_system.short_term_memory)}")
    print(f"Long-term memories: {len(memory_system.long_term_memory)}")
    print(f"Episodes stored: {len(memory_system.episodic_memory)}")
    print(f"Semantic triples: {len(memory_system.semantic_knowledge)}")

if __name__ == "__main__":
    main()

