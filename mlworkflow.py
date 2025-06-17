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



# *************************************************************

Great question! Here are several ways to generate draw.io diagrams programmatically for your banking ML workflow:

## Method 1: Using Python with draw.io XML Generation

```python
import xml.etree.ElementTree as ET
from xml.dom import minidom
import base64
import json

class DrawIOBankingMLDiagram:
    def __init__(self):
        self.colors = {
            'azure': '#0078d4',
            'databricks': '#ff3621',
            'mlflow': '#0194e2',
            'h2o': '#1abc9c',
            'primary': '#1f4e79',
            'secondary': '#2e86ab',
            'accent': '#a23b72',
            'success': '#2d6a4f',
            'warning': '#f77f00'
        }
        
        # Shape styles for different components
        self.styles = {
            'azure_service': f'rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors["azure"]};fontColor=white;strokeColor=white;strokeWidth=2;',
            'databricks': f'rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors["databricks"]};fontColor=white;strokeColor=white;strokeWidth=2;',
            'mlflow': f'rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors["mlflow"]};fontColor=white;strokeColor=white;strokeWidth=2;',
            'h2o': f'rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors["h2o"]};fontColor=white;strokeColor=white;strokeWidth=2;',
            'process': f'rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors["primary"]};fontColor=white;strokeColor=white;strokeWidth=2;',
            'data': f'shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor={self.colors["secondary"]};fontColor=white;',
            'decision': f'rhombus;whiteSpace=wrap;html=1;fillColor={self.colors["warning"]};fontColor=white;strokeColor=white;strokeWidth=2;',
            'flow_arrow': f'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor={self.colors["primary"]};',
            'governance_arrow': f'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor={self.colors["accent"]};dashed=1;'
        }
    
    def create_drawio_xml(self):
        """Generate the complete draw.io XML structure"""
        # Create root mxfile element
        mxfile = ET.Element('mxfile', host="app.diagrams.net", modified="2024-01-01T00:00:00.000Z", agent="Banking ML Workflow Generator")
        
        # Create diagram element
        diagram = ET.SubElement(mxfile, 'diagram', id="banking-ml-workflow", name="Banking ML Workflow")
        
        # Create mxGraphModel
        graph_model = ET.SubElement(diagram, 'mxGraphModel', 
                                   dx="2074", dy="1129", grid="1", gridSize="10", 
                                   guides="1", tooltips="1", connect="1", 
                                   arrows="1", fold="1", page="1", pageScale="1", 
                                   pageWidth="1654", pageHeight="2336", 
                                   math="0", shadow="0")
        
        # Create root cell
        root = ET.SubElement(graph_model, 'root')
        ET.SubElement(root, 'mxCell', id="0")
        ET.SubElement(root, 'mxCell', id="1", parent="0")
        
        # Add all components
        self._add_title_and_legend(root)
        self._add_data_layer(root)
        self._add_compute_layer(root)
        self._add_ml_platform_layer(root)
        self._add_deployment_layer(root)
        self._add_governance_layer(root)
        self._add_workflows(root)
        self._add_connections(root)
        
        return mxfile
    
    def _add_title_and_legend(self, root):
        """Add title and legend to the diagram"""
        # Main title
        title = ET.SubElement(root, 'mxCell', 
                             id="title",
                             value="<h1>Banking ML Platform Architecture - Azure Databricks</h1>",
                             style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=24;fontStyle=1;",
                             vertex="1",
                             parent="1")
        ET.SubElement(title, 'mxGeometry', x="400", y="20", width="800", height="40", **{"as": "geometry"})
        
        # Legend box
        legend_box = ET.SubElement(root, 'mxCell',
                                  id="legend_box",
                                  value="",
                                  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8f9fa;strokeColor=#dee2e6;strokeWidth=2;",
                                  vertex="1",
                                  parent="1")
        ET.SubElement(legend_box, 'mxGeometry', x="50", y="100", width="200", height="300", **{"as": "geometry"})
        
        # Legend title
        legend_title = ET.SubElement(root, 'mxCell',
                                    id="legend_title",
                                    value="<b>Legend</b>",
                                    style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=14;fontStyle=1;",
                                    vertex="1",
                                    parent="1")
        ET.SubElement(legend_title, 'mxGeometry', x="60", y="110", width="180", height="30", **{"as": "geometry"})
        
        # Legend items
        legend_items = [
            ("Azure Services", self.colors['azure']),
            ("Databricks", self.colors['databricks']),
            ("MLflow", self.colors['mlflow']),
            ("H2O.ai", self.colors['h2o']),
            ("Data Storage", self.colors['secondary']),
            ("Governance", self.colors['accent'])
        ]
        
        for i, (label, color) in enumerate(legend_items):
            # Color box
            color_box = ET.SubElement(root, 'mxCell',
                                     id=f"legend_color_{i}",
                                     value="",
                                     style=f"rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=white;strokeWidth=1;",
                                     vertex="1",
                                     parent="1")
            ET.SubElement(color_box, 'mxGeometry', x="70", y=str(150 + i * 25), width="20", height="15", **{"as": "geometry"})
            
            # Label
            color_label = ET.SubElement(root, 'mxCell',
                                       id=f"legend_label_{i}",
                                       value=label,
                                       style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;",
                                       vertex="1",
                                       parent="1")
            ET.SubElement(color_label, 'mxGeometry', x="100", y=str(150 + i * 25), width="140", height="15", **{"as": "geometry"})
    
    def _add_data_layer(self, root):
        """Add data layer components"""
        y_pos = 150
        
        # Data Layer Label
        data_label = ET.SubElement(root, 'mxCell',
                                  id="data_layer_label",
                                  value="<b>Data Layer</b>",
                                  style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;rotation=90;",
                                  vertex="1",
                                  parent="1")
        ET.SubElement(data_label, 'mxGeometry', x="300", y=str(y_pos), width="30", height="200", **{"as": "geometry"})
        
        # Delta Lake
        delta_lake = ET.SubElement(root, 'mxCell',
                                  id="delta_lake",
                                  value="<b>Delta Lake</b><br/>Data Storage<br/>& Versioning",
                                  style=self.styles['data'],
                                  vertex="1",
                                  parent="1")
        ET.SubElement(delta_lake, 'mxGeometry', x="350", y=str(y_pos), width="120", height="80", **{"as": "geometry"})
        
        # Unity Catalog
        unity_catalog = ET.SubElement(root, 'mxCell',
                                     id="unity_catalog",
                                     value="<b>Unity Catalog</b><br/>Data Governance<br/>& Security",
                                     style=self.styles['azure_service'],
                                     vertex="1",
                                     parent="1")
        ET.SubElement(unity_catalog, 'mxGeometry', x="500", y=str(y_pos), width="120", height="80", **{"as": "geometry"})
        
        # Feature Store
        feature_store = ET.SubElement(root, 'mxCell',
                                     id="feature_store",
                                     value="<b>Feature Store</b><br/>Feature Management<br/>& Serving",
                                     style=self.styles['databricks'],
                                     vertex="1",
                                     parent="1")
        ET.SubElement(feature_store, 'mxGeometry', x="650", y=str(y_pos), width="120", height="80", **{"as": "geometry"})
        
        # External Data Sources
        external_data = ET.SubElement(root, 'mxCell',
                                     id="external_data",
                                     value="<b>External Data</b><br/>• Core Banking<br/>• Credit Bureau<br/>• Market Data",
                                     style=self.styles['data'],
                                     vertex="1",
                                     parent="1")
        ET.SubElement(external_data, 'mxGeometry', x="800", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
    
    def _add_compute_layer(self, root):
        """Add compute layer components"""
        y_pos = 270
        
        # Compute Layer Label
        compute_label = ET.SubElement(root, 'mxCell',
                                     id="compute_layer_label",
                                     value="<b>Compute Layer</b>",
                                     style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;rotation=90;",
                                     vertex="1",
                                     parent="1")
        ET.SubElement(compute_label, 'mxGeometry', x="300", y=str(y_pos), width="30", height="200", **{"as": "geometry"})
        
        # Databricks Clusters
        databricks_clusters = ET.SubElement(root, 'mxCell',
                                           id="databricks_clusters",
                                           value="<b>Databricks Clusters</b><br/>• Interactive Clusters<br/>• Job Clusters<br/>• SQL Warehouses",
                                           style=self.styles['databricks'],
                                           vertex="1",
                                           parent="1")
        ET.SubElement(databricks_clusters, 'mxGeometry', x="350", y=str(y_pos), width="150", height="80", **{"as": "geometry"})
        
        # Spark MLlib
        spark_mllib = ET.SubElement(root, 'mxCell',
                                   id="spark_mllib",
                                   value="<b>Spark MLlib</b><br/>Distributed ML<br/>Algorithms",
                                   style=self.styles['process'],
                                   vertex="1",
                                   parent="1")
        ET.SubElement(spark_mllib, 'mxGeometry', x="530", y=str(y_pos), width="120", height="80", **{"as": "geometry"})
        
        # AutoML
        automl = ET.SubElement(root, 'mxCell',
                              id="automl",
                              value="<b>AutoML</b><br/>Automated Model<br/>Development",
                              style=self.styles['h2o'],
                              vertex="1",
                              parent="1")
        ET.SubElement(automl, 'mxGeometry', x="680", y=str(y_pos), width="120", height="80", **{"as": "geometry"})
        
        # H2O Driverless AI
        h2o_dai = ET.SubElement(root, 'mxCell',
                               id="h2o_dai",
                               value="<b>H2O Driverless AI</b><br/>Enterprise AutoML<br/>via Databricks Connect",
                               style=self.styles['h2o'],
                               vertex="1",
                               parent="1")
        ET.SubElement(h2o_dai, 'mxGeometry', x="830", y=str(y_pos), width="160", height="80", **{"as": "geometry"})
    
    def _add_ml_platform_layer(self, root):
        """Add ML platform layer components"""
        y_pos = 390
        
        # ML Platform Label
        ml_label = ET.SubElement(root, 'mxCell',
                                id="ml_platform_label",
                                value="<b>ML Platform</b>",
                                style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;rotation=90;",
                                vertex="1",
                                parent="1")
        ET.SubElement(ml_label, 'mxGeometry', x="300", y=str(y_pos), width="30", height="200", **{"as": "geometry"})
        
        # MLflow
        mlflow = ET.SubElement(root, 'mxCell',
                              id="mlflow",
                              value="<b>MLflow</b><br/>• Experiment Tracking<br/>• Model Registry<br/>• Model Serving",
                              style=self.styles['mlflow'],
                              vertex="1",
                              parent="1")
        ET.SubElement(mlflow, 'mxGeometry', x="350", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
        
        # Databricks Workflows
        workflows = ET.SubElement(root, 'mxCell',
                                 id="workflows",
                                 value="<b>Databricks Workflows</b><br/>Pipeline Orchestration<br/>& Scheduling",
                                 style=self.styles['databricks'],
                                 vertex="1",
                                 parent="1")
        ET.SubElement(workflows, 'mxGeometry', x="520", y=str(y_pos), width="150", height="80", **{"as": "geometry"})
        
        # Model Development
        model_dev = ET.SubElement(root, 'mxCell',
                                 id="model_dev",
                                 value="<b>Model Development</b><br/>• Notebooks<br/>• Collaborative IDE<br/>• Version Control",
                                 style=self.styles['process'],
                                 vertex="1",
                                 parent="1")
        ET.SubElement(model_dev, 'mxGeometry', x="700", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
        
        # GitHub Integration
        github = ET.SubElement(root, 'mxCell',
                              id="github",
                              value="<b>GitHub</b><br/>Code Versioning<br/>& CI/CD",
                              style=self.styles['process'],
                              vertex="1",
                              parent="1")
        ET.SubElement(github, 'mxGeometry', x="870", y=str(y_pos), width="120", height="80", **{"as": "geometry"})
    
    def _add_deployment_layer(self, root):
        """Add deployment layer components"""
        y_pos = 510
        
        # Deployment Layer Label
        deploy_label = ET.SubElement(root, 'mxCell',
                                    id="deploy_layer_label",
                                    value="<b>Deployment</b>",
                                    style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;rotation=90;",
                                    vertex="1",
                                    parent="1")
        ET.SubElement(deploy_label, 'mxGeometry', x="300", y=str(y_pos), width="30", height="200", **{"as": "geometry"})
        
        # Azure ML
        azure_ml = ET.SubElement(root, 'mxCell',
                                id="azure_ml",
                                value="<b>Azure ML</b><br/>Model Deployment<br/>& Management",
                                style=self.styles['azure_service'],
                                vertex="1",
                                parent="1")
        ET.SubElement(azure_ml, 'mxGeometry', x="350", y=str(y_pos), width="120", height="80", **{"as": "geometry"})
        
        # Real-time Endpoints
        realtime_endpoints = ET.SubElement(root, 'mxCell',
                                          id="realtime_endpoints",
                                          value="<b>Real-time Endpoints</b><br/>• REST APIs<br/>• <100ms latency<br/>• Auto-scaling",
                                          style=self.styles['azure_service'],
                                          vertex="1",
                                          parent="1")
        ET.SubElement(realtime_endpoints, 'mxGeometry', x="500", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
        
        # Batch Scoring
        batch_scoring = ET.SubElement(root, 'mxCell',
                                     id="batch_scoring",
                                     value="<b>Batch Scoring</b><br/>• Scheduled Jobs<br/>• Large-scale Inference<br/>• Cost-effective",
                                     style=self.styles['process'],
                                     vertex="1",
                                     parent="1")
        ET.SubElement(batch_scoring, 'mxGeometry', x="670", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
        
        # Model Monitoring
        monitoring = ET.SubElement(root, 'mxCell',
                                  id="monitoring",
                                  value="<b>Model Monitoring</b><br/>• Drift Detection<br/>• Performance Tracking<br/>• Alerts",
                                  style=self.styles['warning'],
                                  vertex="1",
                                  parent="1")
        ET.SubElement(monitoring, 'mxGeometry', x="840", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
    
    def _add_governance_layer(self, root):
        """Add governance and compliance layer"""
        y_pos = 630
        
        # Governance Layer Label
        gov_label = ET.SubElement(root, 'mxCell',
                                 id="gov_layer_label",
                                 value="<b>Governance</b>",
                                 style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;rotation=90;",
                                 vertex="1",
                                 parent="1")
        ET.SubElement(gov_label, 'mxGeometry', x="300", y=str(y_pos), width="30", height="280", **{"as": "geometry"})
        
        # Model Validation
        model_validation = ET.SubElement(root, 'mxCell',
                                        id="model_validation",
                                        value="<b>Model Validation</b><br/>• Independent Review<br/>• Statistical Testing<br/>• Backtesting",
                                        style=f"rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors['accent']};fontColor=white;strokeColor=white;strokeWidth=2;",
                                        vertex="1",
                                        parent="1")
        ET.SubElement(model_validation, 'mxGeometry', x="350", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
        
        # Responsible AI
        responsible_ai = ET.SubElement(root, 'mxCell',
                                      id="responsible_ai",
                                      value="<b>Responsible AI</b><br/>• Fairness Testing<br/>• Explainability<br/>• Bias Detection",
                                      style=f"rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors['accent']};fontColor=white;strokeColor=white;strokeWidth=2;",
                                      vertex="1",
                                      parent="1")
        ET.SubElement(responsible_ai, 'mxGeometry', x="520", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
        
        # Regulatory Compliance
        compliance = ET.SubElement(root, 'mxCell',
                                  id="compliance",
                                  value="<b>Regulatory Compliance</b><br/>• Basel III<br/>• GDPR<br/>• Model Risk Management",
                                  style=f"rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors['accent']};fontColor=white;strokeColor=white;strokeWidth=2;",
                                  vertex="1",
                                  parent="1")
        ET.SubElement(compliance, 'mxGeometry', x="690", y=str(y_pos), width="150", height="80", **{"as": "geometry"})
        
        # Audit Trail
        audit_trail = ET.SubElement(root, 'mxCell',
                                   id="audit_trail",
                                   value="<b>Audit Trail</b><br/>• Decision Logging<br/>• Change Tracking<br/>• Compliance Reports",
                                   style=f"rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors['accent']};fontColor=white;strokeColor=white;strokeWidth=2;",
                                   vertex="1",
                                   parent="1")
        ET.SubElement(audit_trail, 'mxGeometry', x="870", y=str(y_pos), width="140", height="80", **{"as": "geometry"})
    
    def _add_workflows(self, root):
        """Add specific ML workflows"""
        y_pos = 750
        
        # Workflows Label
        workflow_label = ET.SubElement(root, 'mxCell',
                                      id="workflow_label",
                                      value="<b>ML Workflows</b>",
                                      style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;rotation=90;",
                                      vertex="1",
                                      parent="1")
        ET.SubElement(workflow_label, 'mxGeometry', x="300", y=str(y_pos), width="30", height="200", **{"as": "geometry"})
        
        workflows = [
            ("Credit Risk Scoring", "350", "• PD, LGD, EAD Models<br/>• Regulatory Capital<br/>• Risk Rating"),
            ("Product Propensity", "530", "• Cross-sell Models<br/>• Customer Segmentation<br/>• Marketing Optimization"),
            ("Behavior Analysis", "710", "• Transaction Patterns<br/>• Lifecycle Modeling<br/>• Churn Prediction"),
            ("Fraud Detection", "890", "• Real-time Scoring<br/>• Anomaly Detection<br/>• Rule-based Systems")
        ]
        
        for i, (name, x_pos, description) in enumerate(workflows):
            workflow = ET.SubElement(root, 'mxCell',
                                    id=f"workflow_{i}",
                                    value=f"<b>{name}</b><br/>{description}",
                                    style=f"rounded=1;whiteSpace=wrap;html=1;fillColor={self.colors['success']};fontColor=white;strokeColor=white;strokeWidth=2;",
                                    vertex="1",
                                    parent="1")
            ET.SubElement(workflow, 'mxGeometry', x=x_pos, y=str(y_pos), width="150", height="100", **{"as": "geometry"})
    
    def _add_connections(self, root):
        """Add connections between components"""
        connections = [
            # Data flow connections
            ("external_data", "delta_lake", "Data Ingestion"),
            ("delta_lake", "unity_catalog", "Governance"),
            ("unity_catalog", "feature_store", "Feature Management"),
            
            # Compute connections
            ("delta_lake", "databricks_clusters", "Data Access"),
            ("databricks_clusters", "spark_mllib", "ML Processing"),
            ("databricks_clusters", "automl", "AutoML"),
            ("h2o_dai", "databricks_clusters", "Integration"),
            
            # ML Platform connections
            ("spark_mllib", "mlflow", "Experiment Tracking"),
            ("automl", "mlflow", "Model Registry"),
            ("mlflow", "workflows", "Orchestration"),
            ("model_dev", "github", "Version Control"),
            
            # Deployment connections
            ("mlflow", "azure_ml", "Model Deployment"),
            ("azure_ml", "realtime_endpoints", "Real-time Serving"),
            ("azure_ml", "batch_scoring", "Batch Inference"),
            ("realtime_endpoints", "monitoring", "Performance Monitoring"),
            ("batch_scoring", "monitoring", "Drift Detection"),
            
            # Governance connections (dashed lines)
            ("model_validation", "mlflow", "Validation"),
            ("responsible_ai", "azure_ml", "AI Ethics"),
            ("compliance", "monitoring", "Regulatory Monitoring"),
            ("audit_trail", "workflows", "Process Logging")
        ]
        
        connection_id = 1000
        for source, target, label in connections:
            # Determine if it's a governance connection (dashed)
            is_governance = source in ["model_validation", "responsible_ai", "compliance", "audit_trail"]
            style = self.styles['governance_arrow'] if is_governance else self.styles['flow_arrow']
            
            connection = ET.SubElement(root, 'mxCell',
                                      id=str(connection_id),
                                      value=label,
                                      style=style,
                                      edge="1",
                                      parent="1",
                                      source=source,
                                      target=target)
            ET.SubElement(connection, 'mxGeometry', relative="1", **{"as": "geometry"})
            connection_id += 1
    
    def save_to_drawio(self, filename="banking_ml_workflow.drawio"):
        """Save the diagram as a draw.io file"""
        xml_tree = self.create_drawio_xml()
        
        # Pretty print the XML
        rough_string = ET.tostring(xml_tree, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Remove empty lines
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"Draw.io diagram saved as {filename}")
        print(f"Open this file in draw.io (https://app.diagrams.net/) to view and edit the diagram")
        
        return filename
    
    def export_as_drawio_url(self):
        """Generate a draw.io URL that opens the diagram directly"""
        xml_tree = self.create_drawio_xml()
        xml_string = ET.tostring(xml_tree, encoding='utf-8').decode('utf-8')
        
        # Encode the XML for URL
        import urllib.parse
        encoded_xml = urllib.parse.quote(xml_string)
        
        drawio_url = f"https://app.diagrams.net/#R{encoded_xml}"
        
        print("Draw.io URL (click to open diagram directly):")
        print(drawio_url)
        
        return drawio_url


# Usage example
if __name__ == "__main__":
    # Create the diagram generator
    diagram_generator = DrawIOBankingMLDiagram()
    
    # Generate and save the draw.io file
    filename = "banking_ml_workflow_comprehensive.drawio"
    file = diagram_generator.save_to_drawio(filename)
    
    # Also generate a direct URL
    diagram_generator.export_as_drawio_url()
    
    print("\nDiagram Features:")
    print("✓ Complete Azure Databricks architecture")
    print("✓ ML workflow components")
    print("✓ Governance and compliance layer")
    print("✓ AutoML integration (Databricks + H2O)")
    print("✓ Professional banking color scheme")
    print("✓ Detailed component descriptions")
    print("✓ Connection flows and relationships")


## Method 2: Using diagrams-as-code with Graphviz


from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks
from diagrams.azure.ml import MachineLearningServiceWorkspaces
from diagrams.azure.storage import DataLakeStorage
from diagrams.programming.framework import React
from diagrams.programming.language import Python
from diagrams.onprem.analytics import Spark
from diagrams.onprem.database import Postgresql
from diagrams.onprem.vcs import Git

def create_banking_ml_diagram():
    with Diagram("Banking ML Platform - Azure Databricks", show=False, direction="TB"):
        
        # External data sources
        with Cluster("External Data Sources"):
            core_banking = Postgresql("Core Banking")
            credit_bureau = Postgresql("Credit Bureau")
            market_data = Postgresql("Market Data")
        
        # Data layer
        with Cluster("Data Layer"):
            delta_lake = DataLakeStorage("Delta Lake")
            unity_catalog = Databricks("Unity Catalog")
        
        # Compute layer
        with Cluster("Compute & ML Platform"):
            with Cluster("Databricks"):
                databricks_clusters = Databricks("Clusters")
                automl = React("AutoML")
                mlflow = Python("MLflow")
            
            with Cluster("External ML"):
                h2o_dai = Python("H2O Driverless AI")
        
        # Deployment layer
        with Cluster("Deployment"):
            azure_ml = MachineLearningServiceWorkspaces("Azure​​​​​​​​​​​​​​​​...")