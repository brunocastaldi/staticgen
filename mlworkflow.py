import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class BankMLWorkflowVisualizer:
    def __init__(self):
        # Professional banking color scheme
        self.colors = {
            'primary': '#1f4e79',      # Deep blue
            'secondary': '#2e86ab',    # Medium blue
            'accent': '#a23b72',       # Purple accent
            'success': '#2d6a4f',      # Green
            'warning': '#f77f00',      # Orange
            'danger': '#d62828',       # Red
            'azure': '#0078d4',        # Azure blue
            'databricks': '#ff3621',   # Databricks red
            'mlflow': '#0194e2',       # MLflow blue
            'h2o': '#1abc9c',          # H2O teal
            'background': '#f8f9fa',   # Light gray
            'text': '#212529'          # Dark gray
        }
        
        # Component configurations
        self.ml_frameworks = {
            'spark_ml': 'Apache Spark MLlib',
            'synapseml': 'Microsoft SynapseML',
            'lightgbm': 'LightGBM',
            'pycaret': 'PyCaret',
            'h2o3': 'H2O-3',
            'xgboost': 'XGBoost',
            'optuna': 'Optuna',
            'tpot': 'TPOT',
            'databricks_automl': 'Databricks AutoML',
            'h2o_dai': 'H2O Driverless AI'
        }
        
        self.workflow_data = self._initialize_workflow_data()
        
    def _initialize_workflow_data(self):
        """Initialize comprehensive workflow data structure"""
        return {
            'nodes': [],
            'edges': [],
            'workflows': {
                'credit_risk': self._get_credit_risk_workflow(),
                'propensity': self._get_propensity_workflow(),
                'behavior_analysis': self._get_behavior_workflow(),
                'fraud_detection': self._get_fraud_workflow()
            },
            'governance': self._get_governance_workflow(),
            'automl': self._get_automl_workflow()
        }
    
    def _get_credit_risk_workflow(self):
        """Define credit risk scoring pipeline"""
        return {
            'name': 'Credit Risk Scoring Pipeline',
            'description': 'Comprehensive credit risk assessment using ensemble models',
            'components': [
                {
                    'id': 'cr_data_ingestion',
                    'name': 'Data Ingestion',
                    'type': 'data',
                    'platform': 'Delta Lake',
                    'details': {
                        'sources': ['Core Banking', 'Credit Bureau', 'External APIs'],
                        'volume': '10M+ records/day',
                        'latency': 'Near real-time'
                    }
                },
                {
                    'id': 'cr_feature_store',
                    'name': 'Feature Engineering',
                    'type': 'feature',
                    'platform': 'Databricks Feature Store',
                    'details': {
                        'features': ['Payment History', 'Credit Utilization', 'Account Age'],
                        'transformations': ['Rolling Aggregations', 'Categorical Encoding'],
                        'versioning': 'Unity Catalog'
                    }
                },
                {
                    'id': 'cr_model_dev',
                    'name': 'Model Development',
                    'type': 'model',
                    'platform': 'Databricks Notebooks',
                    'details': {
                        'algorithms': ['XGBoost', 'LightGBM', 'Neural Networks'],
                        'validation': 'Time-series cross-validation',
                        'metrics': ['AUC', 'KS', 'Gini', 'PSI']
                    }
                }
            ]
        }
    
    def _get_propensity_workflow(self):
        """Define product propensity modeling workflow"""
        return {
            'name': 'Product Propensity Modeling',
            'description': 'Customer likelihood to purchase financial products',
            'components': [
                {
                    'id': 'pp_segmentation',
                    'name': 'Customer Segmentation',
                    'type': 'analysis',
                    'platform': 'Databricks ML',
                    'details': {
                        'methods': ['K-Means', 'Hierarchical Clustering'],
                        'features': ['Demographics', 'Transaction Patterns', 'Product Holdings'],
                        'segments': ['High Value', 'Growth Potential', 'Risk Averse']
                    }
                },
                {
                    'id': 'pp_modeling',
                    'name': 'Propensity Modeling',
                    'type': 'model',
                    'platform': 'MLflow',
                    'details': {
                        'target_products': ['Credit Cards', 'Personal Loans', 'Mortgages'],
                        'algorithms': ['Random Forest', 'Gradient Boosting'],
                        'calibration': 'Platt Scaling'
                    }
                }
            ]
        }
    
    def _get_behavior_workflow(self):
        """Define customer behavior analysis workflow"""
        return {
            'name': 'Customer Financial Behavior Analysis',
            'description': 'Deep analysis of customer financial patterns and trends',
            'components': [
                {
                    'id': 'cb_time_series',
                    'name': 'Time Series Analysis',
                    'type': 'analysis',
                    'platform': 'Spark MLlib',
                    'details': {
                        'patterns': ['Seasonal Spending', 'Income Cycles', 'Payment Behavior'],
                        'forecasting': 'ARIMA, Prophet, LSTM',
                        'anomaly_detection': 'Isolation Forest'
                    }
                },
                {
                    'id': 'cb_clustering',
                    'name': 'Behavioral Clustering',
                    'type': 'model',
                    'platform': 'Databricks ML',
                    'details': {
                        'dimensions': ['Spending Patterns', 'Channel Preferences', 'Risk Appetite'],
                        'algorithms': ['DBSCAN', 'Gaussian Mixture Models'],
                        'interpretability': 'SHAP, LIME'
                    }
                }
            ]
        }
    
    def _get_fraud_workflow(self):
        """Define real-time fraud detection workflow"""
        return {
            'name': 'Real-time Fraud Detection',
            'description': 'High-frequency fraud detection with sub-second latency',
            'components': [
                {
                    'id': 'fd_streaming',
                    'name': 'Streaming Data Processing',
                    'type': 'streaming',
                    'platform': 'Spark Structured Streaming',
                    'details': {
                        'sources': ['Transaction Streams', 'Device Signals', 'Behavioral Patterns'],
                        'processing': 'Real-time feature computation',
                        'latency': '<100ms'
                    }
                },
                {
                    'id': 'fd_real_time_ml',
                    'name': 'Real-time ML Inference',
                    'type': 'inference',
                    'platform': 'Azure ML',
                    'details': {
                        'models': ['Ensemble Models', 'Deep Learning', 'Rule-based Systems'],
                        'deployment': 'Kubernetes, ACI',
                        'scaling': 'Auto-scaling based on load'
                    }
                }
            ]
        }
    
    def _get_governance_workflow(self):
        """Define governance and compliance workflow"""
        return {
            'name': 'ML Governance & Compliance',
            'description': 'Comprehensive model governance and regulatory compliance',
            'components': [
                {
                    'id': 'gov_validation',
                    'name': 'Model Validation',
                    'type': 'validation',
                    'platform': 'Independent Team',
                    'details': {
                        'validations': ['Statistical Testing', 'Backtesting', 'Stress Testing'],
                        'documentation': 'Model Risk Management',
                        'approval': 'Model Risk Committee'
                    }
                },
                {
                    'id': 'gov_monitoring',
                    'name': 'Model Monitoring',
                    'type': 'monitoring',
                    'platform': 'MLflow + Custom Dashboards',
                    'details': {
                        'metrics': ['Model Drift', 'Data Drift', 'Performance Degradation'],
                        'alerts': 'Real-time notifications',
                        'remediation': 'Automated retraining triggers'
                    }
                },
                {
                    'id': 'gov_responsible_ai',
                    'name': 'Responsible AI',
                    'type': 'ethics',
                    'platform': 'Azure ML Responsible AI',
                    'details': {
                        'fairness': 'Bias detection and mitigation',
                        'explainability': 'Model interpretability',
                        'transparency': 'Decision audit trails'
                    }
                }
            ]
        }
    
    def _get_automl_workflow(self):
        """Define AutoML integration workflow"""
        return {
            'name': 'AutoML Integration',
            'description': 'Automated machine learning with multiple platforms',
            'components': [
                {
                    'id': 'automl_databricks',
                    'name': 'Databricks AutoML',
                    'type': 'automl',
                    'platform': 'Databricks',
                    'details': {
                        'capabilities': ['Classification', 'Regression', 'Forecasting'],
                        'automation': ['Feature Engineering', 'Model Selection', 'Hyperparameter Tuning'],
                        'integration': 'Native MLflow integration'
                    }
                },
                {
                    'id': 'automl_h2o',
                    'name': 'H2O Driverless AI',
                    'type': 'automl',
                    'platform': 'H2O.ai',
                    'details': {
                        'connection': 'Databricks Connect',
                        'features': ['Automatic Feature Engineering', 'Model Interpretability'],
                        'deployment': 'MOJO/POJO scoring pipelines'
                    }
                }
            ]
        }
    
    def create_main_architecture_view(self):
        """Create the main architecture overview"""
        fig = go.Figure()
        
        # Define main architecture components
        components = [
            # Data Layer
            {'name': 'Delta Lake', 'x': 1, 'y': 1, 'type': 'storage', 'size': 40},
            {'name': 'Unity Catalog', 'x': 2, 'y': 1, 'type': 'governance', 'size': 35},
            {'name': 'Feature Store', 'x': 3, 'y': 1, 'type': 'feature', 'size': 35},
            
            # Compute Layer
            {'name': 'Databricks Clusters', 'x': 1, 'y': 2, 'type': 'compute', 'size': 45},
            {'name': 'Spark MLlib', 'x': 2, 'y': 2, 'type': 'ml', 'size': 30},
            {'name': 'AutoML', 'x': 3, 'y': 2, 'type': 'automl', 'size': 30},
            
            # ML Platform Layer
            {'name': 'MLflow', 'x': 1, 'y': 3, 'type': 'mlops', 'size': 40},
            {'name': 'Model Registry in Unity Catalog', 'x': 2, 'y': 3, 'type': 'registry', 'size': 35},
            {'name': 'Databticks Workflows', 'x': 3, 'y': 3, 'type': 'orchestration', 'size': 35},
            
            # Deployment Layer
            {'name': 'Databricks', 'x': 1, 'y': 4, 'type': 'deployment', 'size': 40},
            {'name': 'Real-time Endpoints', 'x': 2, 'y': 4, 'type': 'api', 'size': 35},
            {'name': 'Batch Scoring', 'x': 3, 'y': 4, 'type': 'batch', 'size': 35},
            
            # External Integration
            {'name': 'H2O Driverless AI', 'x': 4, 'y': 2.5, 'type': 'external', 'size': 35},
            {'name': 'GitHub', 'x': 4, 'y': 3.5, 'type': 'version', 'size': 30},
        ]
        
        # Color mapping for component types
        type_colors = {
            'storage': self.colors['azure'],
            'governance': self.colors['primary'],
            'feature': self.colors['secondary'],
            'compute': self.colors['databricks'],
            'ml': self.colors['success'],
            'automl': self.colors['h2o'],
            'mlops': self.colors['mlflow'],
            'registry': self.colors['accent'],
            'orchestration': self.colors['warning'],
            'deployment': self.colors['azure'],
            'api': self.colors['success'],
            'batch': self.colors['secondary'],
            'external': self.colors['h2o'],
            'version': self.colors['text']
        }
        
        # Add components to the plot
        for comp in components:
            fig.add_trace(go.Scatter(
                x=[comp['x']],
                y=[comp['y']],
                mode='markers+text',
                marker=dict(
                    size=comp['size'],
                    color=type_colors[comp['type']],
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                text=[comp['name']],
                textposition="middle center",
                textfont=dict(color='white', size=10, family='Arial Black'),
                name=comp['type'].title(),
                hovertemplate=f"<b>{comp['name']}</b><br>Type: {comp['type'].title()}<br><extra></extra>",
                showlegend=False
            ))
        
        # Add connections between components
        connections = [
            # Data flow connections
            (1, 1, 1, 2),  # Delta Lake to Databricks
            (2, 1, 2, 2),  # Unity Catalog to Spark
            (3, 1, 3, 2),  # Feature Store to AutoML
            
            # ML pipeline connections
            (1, 2, 1, 3),  # Databricks to MLflow
            (2, 2, 2, 3),  # Spark to Model Registry
            (3, 2, 3, 3),  # AutoML to Workflows
            
            # Deployment connections
            (1, 3, 1, 4),  # MLflow to Azure ML
            (2, 3, 2, 4),  # Model Registry to Endpoints
            (3, 3, 3, 4),  # Workflows to Batch Scoring
            
            # External connections
            (4, 2.5, 2, 2),  # H2O to Spark
            (4, 3.5, 2, 3),  # GitHub to Model Registry
        ]
        
        for x1, y1, x2, y2 in connections:
            fig.add_trace(go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode='lines',
                line=dict(color=self.colors['text'], width=2, dash='dot'),
                opacity=0.6,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="<b>Banking ML Platform Architecture - Azure Databricks</b>",
                x=0.5,
                font=dict(size=20, color=self.colors['primary'])
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                range=[0.5, 4.5]
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                range=[0.5, 4.5]
            ),
            annotations=[
                dict(
                    text="Data Layer",
                    x=0.3, y=1,
                    showarrow=False,
                    font=dict(size=12, color=self.colors['primary']),
                    textangle=90
                ),
                dict(
                    text="Compute Layer",
                    x=0.3, y=2,
                    showarrow=False,
                    font=dict(size=12, color=self.colors['primary']),
                    textangle=90
                ),
                dict(
                    text="ML Platform",
                    x=0.3, y=3,
                    showarrow=False,
                    font=dict(size=12, color=self.colors['primary']),
                    textangle=90
                ),
                dict(
                    text="Deployment",
                    x=0.3, y=4,
                    showarrow=False,
                    font=dict(size=12, color=self.colors['primary']),
                    textangle=90
                )
            ],
            height=600,
            width=900
        )
        
        return fig
    
    def create_workflow_detail_view(self, workflow_name):
        """Create detailed view of a specific workflow"""
        workflow = self.workflow_data['workflows'].get(workflow_name)
        if not workflow:
            return None
        
        fig = go.Figure()
        
        # Define workflow stages with positions
        stages = [
            {'name': 'Data Ingestion', 'x': 1, 'y': 3, 'phase': 'data'},
            {'name': 'Data Validation', 'x': 2, 'y': 3, 'phase': 'validation'},
            {'name': 'Feature Engineering', 'x': 3, 'y': 3, 'phase': 'feature'},
            {'name': 'Model Training', 'x': 4, 'y': 3, 'phase': 'training'},
            {'name': 'Model Validation', 'x': 5, 'y': 3, 'phase': 'validation'},
            {'name': 'Model Deployment', 'x': 6, 'y': 3, 'phase': 'deployment'},
            {'name': 'Monitoring', 'x': 7, 'y': 3, 'phase': 'monitoring'},
            
            # Governance layer
            {'name': 'Risk Assessment', 'x': 2, 'y': 4, 'phase': 'governance'},
            {'name': 'Compliance Check', 'x': 4, 'y': 4, 'phase': 'governance'},
            {'name': 'Audit Trail', 'x': 6, 'y': 4, 'phase': 'governance'},
            
            # AutoML alternatives
            {'name': 'AutoML Option', 'x': 4, 'y': 2, 'phase': 'automl'},
            {'name': 'H2O Driverless AI', 'x': 5, 'y': 2, 'phase': 'automl'}
        ]
        
        phase_colors = {
            'data': self.colors['azure'],
            'validation': self.colors['warning'],
            'feature': self.colors['secondary'],
            'training': self.colors['success'],
            'deployment': self.colors['databricks'],
            'monitoring': self.colors['accent'],
            'governance': self.colors['primary'],
            'automl': self.colors['h2o']
        }
        
        # Add workflow stages
        for stage in stages:
            fig.add_trace(go.Scatter(
                x=[stage['x']],
                y=[stage['y']],
                mode='markers+text',
                marker=dict(
                    size=40,
                    color=phase_colors[stage['phase']],
                    line=dict(width=2, color='white')
                ),
                text=[stage['name']],
                textposition="middle center",
                textfont=dict(color='white', size=9, family='Arial'),
                name=stage['phase'].title(),
                hovertemplate=f"<b>{stage['name']}</b><br>Phase: {stage['phase'].title()}<br><extra></extra>",
                showlegend=False
            ))
        
        # Add flow arrows
        main_flow = [(1,3,2,3), (2,3,3,3), (3,3,4,3), (4,3,5,3), (5,3,6,3), (6,3,7,3)]
        governance_flow = [(2,4,4,4), (4,4,6,4)]
        automl_flow = [(4,2,5,2), (4,2,4,3), (5,2,5,3)]
        
        all_flows = [
            (main_flow, 'solid', self.colors['primary']),
            (governance_flow, 'dash', self.colors['accent']),
            (automl_flow, 'dot', self.colors['h2o'])
        ]
        
        for flows, line_style, color in all_flows:
            for x1, y1, x2, y2 in flows:
                fig.add_trace(go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode='lines',
                    line=dict(color=color, width=3, dash=line_style),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Add arrow heads
                fig.add_annotation(
                    x=x2, y=y2,
                    ax=x1, ay=y1,
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=color
                )
        
        fig.update_layout(
            title=dict(
                text=f"<b>{workflow['name']} - Detailed Workflow</b>",
                x=0.5,
                font=dict(size=18, color=self.colors['primary'])
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                range=[0.5, 7.5]
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                range=[1.5, 4.5]
            ),
            height=500,
            width=1000,
            annotations=[
                dict(
                    text="Main ML Pipeline",
                    x=4, y=1.8,
                    showarrow=False,
                    font=dict(size=12, color=self.colors['primary'])
                ),
                dict(
                    text="AutoML Alternative",
                    x=4.5, y=1.5,
                    showarrow=False,
                    font=dict(size=10, color=self.colors['h2o'])
                ),
                dict(
                    text="Governance & Compliance",
                    x=4, y=4.3,
                    showarrow=False,
                    font=dict(size=10, color=self.colors['accent'])
                )
            ]
        )
        
        return fig
    
    def create_timeline_view(self):
        """Create timeline view of development to production lifecycle"""
        # Sample timeline data
        timeline_data = [
            {'Task': 'Data Collection & Preparation', 'Start': '2024-01-01', 'Finish': '2024-01-15', 'Phase': 'Data'},
            {'Task': 'Feature Engineering', 'Start': '2024-01-10', 'Finish': '2024-01-25', 'Phase': 'Feature'},
            {'Task': 'Model Development', 'Start': '2024-01-20', 'Finish': '2024-02-10', 'Phase': 'Development'},
            {'Task': 'AutoML Experiments', 'Start': '2024-01-25', 'Finish': '2024-02-05', 'Phase': 'AutoML'},
            {'Task': 'Model Validation', 'Start': '2024-02-05', 'Finish': '2024-02-20', 'Phase': 'Validation'},
            {'Task': 'A/B Testing', 'Start': '2024-02-15', 'Finish': '2024-03-01', 'Phase': 'Testing'},
            {'Task': 'Production Deployment', 'Start': '2024-02-25', 'Finish': '2024-03-10', 'Phase': 'Deployment'},
            {'Task': 'Monitoring & Maintenance', 'Start': '2024-03-01', 'Finish': '2024-12-31', 'Phase': 'Operations'}
        ]
        
        df = pd.DataFrame(timeline_data)
        df['Start'] = pd.to_datetime(df['Start'])
        df['Finish'] = pd.to_datetime(df['Finish'])
        
        phase_colors = {
            'Data': self.colors['azure'],
            'Feature': self.colors['secondary'],
            'Development': self.colors['success'],
            'AutoML': self.colors['h2o'],
            'Validation': self.colors['warning'],
            'Testing': self.colors['accent'],
            'Deployment': self.colors['databricks'],
            'Operations': self.colors['primary']
        }
        
        fig = go.Figure()
        
        for i, row in df.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['Start'], row['Finish']],
                y=[i, i],
                mode='lines+markers',
                line=dict(color=phase_colors[row['Phase']], width=8),
                marker=dict(size=8, color=phase_colors[row['Phase']]),
                name=row['Phase'],
                text=[row['Task'], row['Task']],
                hovertemplate=f"<b>{row['Task']}</b><br>Start: {row['Start'].strftime('%Y-%m-%d')}<br>End: {row['Finish'].strftime('%Y-%m-%d')}<br>Phase: {row['Phase']}<extra></extra>",
                showlegend=False
            ))
        
        fig.update_layout(
            title=dict(
                text="<b>ML Project Timeline - Development to Production</b>",
                x=0.5,
                font=dict(size=18, color=self.colors['primary'])
            ),
            xaxis=dict(
                title="Timeline",
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title="Project Tasks",
                tickvals=list(range(len(df))),
                ticktext=df['Task'].tolist(),
                showgrid=True,
                gridcolor='lightgray'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=600,
            width=1000
        )
        
        return fig
    
    def create_cost_optimization_view(self):
        """Create resource allocation and cost optimization visualization"""
        # Sample cost data
        cost_data = {
            'Component': ['Databricks Compute', 'Delta Lake Storage', 'MLflow Tracking', 
                         'Feature Store', 'Model Serving', 'H2O Driverless AI', 'Monitoring'],
            'Monthly_Cost': [15000, 3000, 1500, 2000, 5000, 8000, 2500],
            'Utilization': [85, 70, 90, 75, 60, 40, 95],
            'Optimization_Potential': [10, 25, 5, 15, 30, 50, 5]
        }
        
        df = pd.DataFrame(cost_data)
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Cost Distribution', 'Utilization vs Cost', 
                          'Optimization Potential', 'Cost Trend'),
            specs=[[{"type": "pie"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Pie chart for cost distribution
        fig.add_trace(
            go.Pie(
                labels=df['Component'],
                values=df['Monthly_Cost'],
                hole=0.4,
                marker_colors=[self.colors['azure'], self.colors['secondary'], 
                              self.colors['mlflow'], self.colors['success'],
                              self.colors['databricks'], self.colors['h2o'], 
                              self.colors['accent']]
            ),
            row=1, col=1
        )
        
        # Scatter plot for utilization vs cost
        fig.add_trace(
            go.Scatter(
                x=df['Monthly_Cost'],
                y=df['Utilization'],
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=df['Optimization_Potential'],
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="Optimization<br>Potential (%)")
                ),
                text=df['Component'],
                textposition="top center",
                hovertemplate="<b>%{text}</b><br>Cost: $%{x:,.0f}<br>Utilization: %{y}%<extra></extra>"
            ),
            row=1, col=2
        )
        
        # Bar chart for optimization potential
        fig.add_trace(
            go.Bar(
                x=df['Component'],
                y=df['Optimization_Potential'],
                marker_color=[self.colors['success'] if x < 20 else self.colors['warning'] if x < 40 else self.colors['danger'] 
                             for x in df['Optimization_Potential']],
                text=df['Optimization_Potential'],
                texttemplate='%{text}%',
                textposition='outside'
            ),
            row=2, col=1
        )
        
        # Cost trend simulation
        months = pd.date_range('2024-01-01', periods=12, freq='M')
        baseline_cost = 37000
        optimized_cost = [baseline_cost * (1 - 0.02 * i) for i in range(12)]  # 2% monthly reduction
        
        fig.add_trace(
            go.Scatter(
                x=months,
                y=[baseline_cost] * 12,
                mode='lines',
                name='Current Cost',
                line=dict(color=self.colors['danger'], dash='dash')
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=months,
                y=optimized_cost,
                mode='lines+markers',
                name='Optimized Cost',
                line=dict(color=self.colors['success']),
                fill='tonexty',
                fillcolor=f"rgba{tuple(list(px.colors.hex_to_rgb(self.colors['success'])) + [0.2])}"
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title=dict(
                text="<b>ML Platform Cost Optimization Dashboard</b>",
                x=0.5,
                font=dict(size=18, color=self.colors['primary'])
            ),
            height=800,
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Update subplot titles and axes
        fig.update_xaxes(title_text="Monthly Cost ($)", row=1, col=2)
        fig.update_yaxes(title_text="Utilization (%)", row=1, col=2)
        fig.update_xaxes(title_text="Component", row=2, col=1)
        fig.update_yaxes(title_text="Optimization Potential (%)", row=2, col=1)
        fig.update_xaxes(title_text="Month", row=2, col=2)
        fig.update_yaxes(title_text="Cost ($)", row=2, col=2)
        
        return fig
    
    def create_interactive_dashboard(self):
        """Create the main interactive dashboard with all views"""
        # This would typically use Plotly Dash for full interactivity
        # For now, we'll create individual figures that can be displayed
        
        dashboard_components = {
            'architecture': self.create_main_architecture_view(),
            'credit_risk_workflow': self.create_workflow_detail_view('credit_risk'),
            'propensity_workflow': self.create_workflow_detail_view('propensity'),
            'behavior_workflow': self.create_workflow_detail_view('behavior_analysis'),
            'fraud_workflow': self.create_workflow_detail_view('fraud_detection'),
            'timeline': self.create_timeline_view(),
            'cost_optimization': self.create_cost_optimization_view()
        }
        
        return dashboard_components
    
    def create_ml_framework_comparison(self):
        """Create comparison view of different ML frameworks"""
        frameworks_data = {
            'Framework': list(self.ml_frameworks.keys()),
            'Performance': [8.5, 9.0, 9.2, 7.8, 8.8, 9.1, 8.0, 7.5, 8.7, 9.5],
            'Ease_of_Use': [7.0, 8.5, 8.8, 9.5, 8.0, 7.5, 7.8, 8.2, 9.0, 9.8],
            'Scalability': [9.5, 9.2, 8.5, 7.0, 8.8, 8.7, 7.5, 7.2, 8.5, 9.0],
            'Integration': [9.0, 9.5, 8.0, 8.5, 7.5, 8.0, 8.2, 7.8, 9.5, 8.8]
        }
        
        df = pd.DataFrame(frameworks_data)
        
        fig = go.Figure()
        
        # Create radar chart for each framework
        categories = ['Performance', 'Ease of Use', 'Scalability', 'Integration']
        
        # Add traces for top 5 frameworks
        top_frameworks = ['databricks_automl', 'h2o_dai', 'lightgbm', 'synapseml', 'xgboost']
        colors = [self.colors['databricks'], self.colors['h2o'], self.colors['success'], 
                 self.colors['azure'], self.colors['accent']]
        
        for i, fw in enumerate(top_frameworks):
            fw_data = df[df['Framework'] == fw].iloc[0]
            values = [fw_data['Performance'], fw_data['Ease_of_Use'], 
                     fw_data['Scalability'], fw_data['Integration']]
            
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # Close the polygon
                theta=categories + [categories[0]],
                fill='toself',
                name=self.ml_frameworks[fw],
                line_color=colors[i],
                fillcolor=f"rgba{tuple(list(px.colors.hex_to_rgb(colors[i])) + [0.2])}"
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            title=dict(
                text="<b>ML Framework Comparison - Banking Use Cases</b>",
                x=0.5,
                font=dict(size=18, color=self.colors['primary'])
            ),
            height=600,
            showlegend=True
        )
        
        return fig
    
    def export_to_html(self, dashboard_components, filename="banking_ml_dashboard.html"):
        """Export all visualizations to an interactive HTML file"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Banking ML Workflow Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    text-align: center;
                    color: {self.colors['primary']};
                    margin-bottom: 30px;
                }}
                .section {{
                    background: white;
                    margin: 20px 0;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .nav-buttons {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .nav-button {{
                    background-color: {self.colors['primary']};
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    margin: 0 10px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                }}
                .nav-button:hover {{
                    background-color: {self.colors['secondary']};
                }}
                .chart-container {{
                    width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Banking ML Workflow Dashboard</h1>
                <h2>Azure Databricks Platform Architecture</h2>
            </div>
            
            <div class="nav-buttons">
                <button class="nav-button" onclick="showSection('architecture')">Architecture</button>
                <button class="nav-button" onclick="showSection('workflows')">Workflows</button>
                <button class="nav-button" onclick="showSection('timeline')">Timeline</button>
                <button class="nav-button" onclick="showSection('costs')">Cost Analysis</button>
                <button class="nav-button" onclick="showSection('frameworks')">Frameworks</button>
            </div>
        """
        
        # Add each dashboard component
        for name, fig in dashboard_components.items():
            if fig:
                html_content += f"""
                <div id="{name}" class="section chart-container">
                    <div id="plot_{name}"></div>
                </div>
                """
        
        # Add framework comparison
        framework_fig = self.create_ml_framework_comparison()
        html_content += f"""
        <div id="frameworks" class="section chart-container">
            <div id="plot_frameworks"></div>
        </div>
        """
        
        # Add JavaScript for interactivity
        html_content += """
        <script>
            // Plot all charts
        """
        
        for name, fig in dashboard_components.items():
            if fig:
                html_content += f"""
                Plotly.newPlot('plot_{name}', {fig.to_json()}, {{}});
                """
        
        html_content += f"""
            Plotly.newPlot('plot_frameworks', {framework_fig.to_json()}, {{}});
            
            // Navigation functionality
            function showSection(sectionName) {{
                const sections = ['architecture', 'workflows', 'timeline', 'costs', 'frameworks'];
                sections.forEach(section => {{
                    document.getElementById(section).style.display = 'none';
                }});
                
                if (sectionName === 'workflows') {{
                    ['credit_risk_workflow', 'propensity_workflow', 'behavior_workflow', 'fraud_workflow'].forEach(workflow => {{
                        const element = document.getElementById(workflow);
                        if (element) element.style.display = 'block';
                    }});
                }} else if (sectionName === 'costs') {{
                    document.getElementById('cost_optimization').style.display = 'block';
                }} else {{
                    const element = document.getElementById(sectionName);
                    if (element) element.style.display = 'block';
                }}
            }}
            
            // Show architecture by default
            showSection('architecture');
        </script>
        </body>
        </html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Dashboard exported to {filename}")


# Usage Example
if __name__ == "__main__":
    # Initialize the visualizer
    visualizer = BankMLWorkflowVisualizer()
    
    # Create all dashboard components
    dashboard = visualizer.create_interactive_dashboard()
    
    # Display individual components (in Jupyter notebook)
    print("Banking ML Workflow Visualization Created!")
    print("\nAvailable dashboard components:")
    for component_name in dashboard.keys():
        print(f"- {component_name}")
    
    # Export to HTML for presentation
    visualizer.export_to_html(dashboard)
    
    # Example: Display the main architecture view
    if dashboard['architecture']:
        dashboard['architecture'].show()