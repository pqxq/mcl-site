"""
Wagtail hooks to fix admin dashboard issues with IndexEntry workflow states
and customize the page type chooser.
"""
from django.utils.html import format_html
from wagtail import hooks


@hooks.register('insert_global_admin_css')
def add_page_chooser_styles():
    """Add custom CSS for page type chooser with separator"""
    return format_html('''
        <style>
            /* Separator styling for page type groups */
            .page-type-group-header {{
                font-size: 0.75rem;
                color: #666;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 0.75rem 1rem;
                background: #f0f0f0;
                margin: 0;
                border-bottom: 1px solid #ddd;
            }}
            
            .page-type-group-header.content-pages {{
                margin-top: 1rem;
                border-top: 2px solid #1e3a5f;
            }}
            
            /* Hide system pages that already exist */
            .page-type-hidden {{
                display: none !important;
            }}
        </style>
    ''')


@hooks.register('insert_global_admin_js')
def add_page_type_separator_js():
    """Add JavaScript to create visual separator between system and content page types"""
    return format_html('''
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Run on page load and also observe for dynamically loaded content
            function addPageTypeSeparators() {{
                // Find the page type chooser list (on add_subpage view)
                const pageTypeLists = document.querySelectorAll('.listing, [class*="page-type"]');
                
                // Look for the specific add subpage page
                const pageTypeLinks = document.querySelectorAll('a[href*="/admin/pages/add/"]');
                if (pageTypeLinks.length === 0) return;
                
                // Get the parent container
                let listContainer = null;
                pageTypeLinks.forEach(link => {{
                    const parent = link.closest('ul, .w-grid');
                    if (parent && !parent.dataset.separated) {{
                        listContainer = parent;
                    }}
                }});
                
                if (!listContainer || listContainer.dataset.separated) return;
                listContainer.dataset.separated = 'true';
                
                // System page types that should appear first
                const systemPageTypes = [
                    'aboutpage',
                    'newsindexpage', 
                    'staffindexpage',
                    'documentsindexpage',
                    'applicationformpage',
                    'schedulepage'
                ];
                
                // Get all page type items
                const items = Array.from(listContainer.querySelectorAll('li, .w-grid__item'));
                if (items.length === 0) return;
                
                const systemItems = [];
                const contentItems = [];
                
                items.forEach(item => {{
                    const link = item.querySelector('a[href*="/admin/pages/add/"]');
                    if (link) {{
                        const href = link.getAttribute('href').toLowerCase();
                        const isSystem = systemPageTypes.some(type => href.includes(type));
                        if (isSystem) {{
                            systemItems.push(item);
                        }} else {{
                            contentItems.push(item);
                        }}
                    }}
                }});
                
                // Only add separators if we have both types
                if (systemItems.length > 0 && contentItems.length > 0) {{
                    // Create system header
                    const systemHeader = document.createElement('li');
                    systemHeader.className = 'page-type-group-header';
                    systemHeader.textContent = '⚙️ Системні розділи';
                    systemHeader.style.cssText = 'list-style: none; font-size: 0.75rem; color: #666; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 0.75rem 1rem; background: #f0f0f0; margin: 0; border-bottom: 1px solid #ddd;';
                    
                    // Create content header  
                    const contentHeader = document.createElement('li');
                    contentHeader.className = 'page-type-group-header content-pages';
                    contentHeader.textContent = '📄 Сторінки контенту';
                    contentHeader.style.cssText = 'list-style: none; font-size: 0.75rem; color: #666; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 0.75rem 1rem; background: #e8f4e8; margin-top: 1.5rem; border-top: 3px solid #1e3a5f; border-bottom: 1px solid #ddd;';
                    
                    // Clear and rebuild the list
                    listContainer.innerHTML = '';
                    
                    // Add system section
                    listContainer.appendChild(systemHeader);
                    systemItems.forEach(item => listContainer.appendChild(item));
                    
                    // Add content section
                    listContainer.appendChild(contentHeader);
                    contentItems.forEach(item => listContainer.appendChild(item));
                }}
            }}
            
            // Run on page load
            setTimeout(addPageTypeSeparators, 100);
            
            // Also observe for dynamic content changes
            const observer = new MutationObserver(function(mutations) {{
                setTimeout(addPageTypeSeparators, 100);
            }});
            
            observer.observe(document.body, {{
                childList: true,
                subtree: true
            }});
        }});
        </script>
    ''')


@hooks.register('construct_page_listing_buttons')
def add_page_type_descriptions(buttons, page, user, context=None, **kwargs):
    """No modification needed for listing buttons"""
    return buttons


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

