"""
Channel Management System with Spaces and Tabs
Organizes RCM workflow by payer, branch, and function
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import db, TimestampMixin


class ChannelType(str, Enum):
    """Types of channels"""
    PAYER = 'payer'  # Payer-specific channels (Bupa, MOH, etc.)
    BRANCH = 'branch'  # Branch-specific channels (Khamis, Riyadh, etc.)
    FUNCTION = 'function'  # Function channels (Rejections, Resubmissions, etc.)
    WORKFLOW = 'workflow'  # Workflow stages
    TEAM = 'team'  # Team collaboration


class TabType(str, Enum):
    """Types of tabs within channels"""
    OVERVIEW = 'overview'
    CLAIMS = 'claims'
    REJECTIONS = 'rejections'
    RESUBMISSIONS = 'resubmissions'
    ANALYTICS = 'analytics'
    DOCUMENTS = 'documents'
    TASKS = 'tasks'
    TIMELINE = 'timeline'
    REPORTS = 'reports'
    SETTINGS = 'settings'


class Channel(db.Model, TimestampMixin):
    """Channel model for organizing workflow"""
    __tablename__ = 'channels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    # Channel type and configuration
    channel_type = db.Column(db.Enum(ChannelType), nullable=False)
    icon = db.Column(db.String(10), nullable=True)
    color = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Associations
    payer_id = db.Column(db.String(50), nullable=True)  # Links to payer
    branch_name = db.Column(db.String(50), nullable=True)  # Links to branch
    
    # Organization
    parent_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=True)
    order = db.Column(db.Integer, default=0)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    is_private = db.Column(db.Boolean, default=False)
    settings = db.Column(db.JSON, nullable=True)
    
    # Relationships
    parent = db.relationship('Channel', remote_side=[id], backref='subchannels')
    spaces = db.relationship('Space', backref='channel', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Channel {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'channel_type': self.channel_type.value if isinstance(self.channel_type, ChannelType) else self.channel_type,
            'icon': self.icon,
            'color': self.color,
            'description': self.description,
            'payer_id': self.payer_id,
            'branch_name': self.branch_name,
            'parent_id': self.parent_id,
            'order': self.order,
            'is_active': self.is_active,
            'is_private': self.is_private,
            'settings': self.settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Space(db.Model, TimestampMixin):
    """Space model - containers within channels"""
    __tablename__ = 'spaces'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(10), nullable=True)
    
    # Organization
    order = db.Column(db.Integer, default=0)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    settings = db.Column(db.JSON, nullable=True)
    
    # Relationships
    tabs = db.relationship('Tab', backref='space', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Space {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'order': self.order,
            'is_active': self.is_active,
            'settings': self.settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Tab(db.Model, TimestampMixin):
    """Tab model - specific views within spaces"""
    __tablename__ = 'tabs'
    
    id = db.Column(db.Integer, primary_key=True)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    tab_type = db.Column(db.Enum(TabType), nullable=False)
    icon = db.Column(db.String(10), nullable=True)
    
    # Configuration
    view_config = db.Column(db.JSON, nullable=True)  # View-specific configuration
    filters = db.Column(db.JSON, nullable=True)  # Default filters
    
    # Organization
    order = db.Column(db.Integer, default=0)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Tab {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'space_id': self.space_id,
            'name': self.name,
            'slug': self.slug,
            'tab_type': self.tab_type.value if isinstance(self.tab_type, TabType) else self.tab_type,
            'icon': self.icon,
            'view_config': self.view_config,
            'filters': self.filters,
            'order': self.order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ChannelManager:
    """Manage channels, spaces, and tabs"""
    
    @staticmethod
    def create_payer_channel(payer_config: Dict[str, Any]) -> Channel:
        """
        Create a channel for a specific payer
        
        Args:
            payer_config: Payer configuration from PayerConfig
            
        Returns:
            Created channel
        """
        channel = Channel(
            name=payer_config['name'],
            slug=payer_config['id'].lower(),
            channel_type=ChannelType.PAYER,
            icon=payer_config.get('icon', '🏥'),
            color=payer_config.get('color'),
            payer_id=payer_config['id'],
            description=f"Channel for {payer_config['name']} claims management",
            settings={
                'api_endpoint': payer_config.get('api_endpoint'),
                'portal_url': payer_config.get('portal_url'),
                'turnaround_time': payer_config.get('turnaround_time'),
                'submission_methods': payer_config.get('submission_methods', [])
            }
        )
        
        db.session.add(channel)
        db.session.commit()
        
        # Create default spaces
        ChannelManager._create_default_spaces(channel, payer_config)
        
        return channel
    
    @staticmethod
    def _create_default_spaces(channel: Channel, payer_config: Dict[str, Any]):
        """Create default spaces for a payer channel"""
        
        # Create spaces for each branch
        for i, branch in enumerate(payer_config.get('branches', [])):
            space = Space(
                channel_id=channel.id,
                name=f"{branch} Branch",
                slug=f"{channel.slug}-{branch.lower()}",
                icon='🏢',
                order=i,
                settings={'branch': branch}
            )
            db.session.add(space)
            db.session.commit()
            
            # Create default tabs for each space
            ChannelManager._create_default_tabs(space)
        
        # Create overview space
        overview_space = Space(
            channel_id=channel.id,
            name="Overview",
            slug=f"{channel.slug}-overview",
            icon='📊',
            order=-1
        )
        db.session.add(overview_space)
        db.session.commit()
        ChannelManager._create_default_tabs(overview_space)
    
    @staticmethod
    def _create_default_tabs(space: Space):
        """Create default tabs for a space"""
        default_tabs = [
            {'name': 'Overview', 'type': TabType.OVERVIEW, 'icon': '📊', 'order': 0},
            {'name': 'Active Claims', 'type': TabType.CLAIMS, 'icon': '📋', 'order': 1},
            {'name': 'Rejections', 'type': TabType.REJECTIONS, 'icon': '⚠️', 'order': 2},
            {'name': 'Resubmissions', 'type': TabType.RESUBMISSIONS, 'icon': '🔄', 'order': 3},
            {'name': 'Documents', 'type': TabType.DOCUMENTS, 'icon': '📄', 'order': 4},
            {'name': 'Analytics', 'type': TabType.ANALYTICS, 'icon': '📈', 'order': 5},
            {'name': 'Timeline', 'type': TabType.TIMELINE, 'icon': '⏱️', 'order': 6},
        ]
        
        for tab_config in default_tabs:
            tab = Tab(
                space_id=space.id,
                name=tab_config['name'],
                slug=f"{space.slug}-{tab_config['name'].lower().replace(' ', '-')}",
                tab_type=tab_config['type'],
                icon=tab_config['icon'],
                order=tab_config['order']
            )
            db.session.add(tab)
        
        db.session.commit()
    
    @staticmethod
    def get_channel_hierarchy() -> Dict[str, Any]:
        """Get complete channel hierarchy"""
        channels = Channel.query.filter_by(parent_id=None, is_active=True).order_by(Channel.order).all()
        
        hierarchy = []
        for channel in channels:
            channel_data = channel.to_dict()
            channel_data['spaces'] = []
            
            for space in channel.spaces:
                if space.is_active:
                    space_data = space.to_dict()
                    space_data['tabs'] = [tab.to_dict() for tab in space.tabs if tab.is_active]
                    channel_data['spaces'].append(space_data)
            
            hierarchy.append(channel_data)
        
        return {'channels': hierarchy}
    
    @staticmethod
    def initialize_system_channels():
        """Initialize channels for all configured payers"""
        from rcm_config import PayerConfig
        
        # Create primary payer channels
        for payer_config in PayerConfig.get_primary_payers():
            existing = Channel.query.filter_by(payer_id=payer_config['id']).first()
            if not existing:
                print(f"Creating channel for {payer_config['name']}...")
                ChannelManager.create_payer_channel(payer_config)
        
        # Create function channels
        ChannelManager._create_function_channels()
    
    @staticmethod
    def _create_function_channels():
        """Create function-based channels"""
        function_channels = [
            {
                'name': 'Rejection Management',
                'slug': 'rejection-management',
                'icon': '⚠️',
                'color': '#FF4444',
                'description': 'Centralized rejection tracking and resolution'
            },
            {
                'name': 'Resubmission Hub',
                'slug': 'resubmission-hub',
                'icon': '🔄',
                'color': '#4CAF50',
                'description': 'Manage claim resubmissions and appeals'
            },
            {
                'name': 'Reconciliation',
                'slug': 'reconciliation',
                'icon': '💰',
                'color': '#2196F3',
                'description': 'Payment reconciliation and AR management'
            }
        ]
        
        for config in function_channels:
            existing = Channel.query.filter_by(slug=config['slug']).first()
            if not existing:
                channel = Channel(
                    name=config['name'],
                    slug=config['slug'],
                    channel_type=ChannelType.FUNCTION,
                    icon=config['icon'],
                    color=config['color'],
                    description=config['description']
                )
                db.session.add(channel)
        
        db.session.commit()
