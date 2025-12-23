"""
Wagtail hooks to fix admin dashboard issues with IndexEntry workflow states
"""
from wagtail import hooks


@hooks.register('construct_homepage_panels')
def fix_recently_edited_panel(request, panels):
    """
    Fix the recently edited panel to avoid IndexEntry workflow states error.
    This wraps the panel's get_context_data to handle the AttributeError gracefully.
    """
    filtered_panels = []
    for panel in panels:
        # Check if this is the problematic "Recently edited" panel
        # The error occurs in wagtail/admin/views/home.py when trying to
        # prefetch _specific_workflow_states on IndexEntry objects
        panel_name = getattr(panel, 'name', '')
        if panel_name == 'recently_edited':
            # Wrap the panel to catch and handle the error
            original_get_context = panel.get_context_data
            
            def safe_get_context(parent_context):
                try:
                    return original_get_context(parent_context)
                except AttributeError as e:
                    if '_specific_workflow_states' in str(e):
                        # Return empty context for this panel to avoid the error
                        return {}
                    raise
            
            panel.get_context_data = safe_get_context
        
        filtered_panels.append(panel)
    
    return filtered_panels

