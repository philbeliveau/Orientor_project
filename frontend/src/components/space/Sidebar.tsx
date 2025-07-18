import { Recommendation } from '@/services/spaceService';

interface SidebarProps {
  items: Recommendation[];
  selectedId?: number;
  onSelect: (item: Recommendation) => void;
  onDelete: (item: Recommendation) => void;
  loading: boolean;
  error: string | null;
}

export default function Sidebar({ items, selectedId, onSelect, onDelete, loading, error }: SidebarProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2" style={{ borderColor: 'var(--accent)' }}></div>
      </div>
    );
  }

  if (error) {
    return <div className="text-center p-4" style={{ color: '#ef4444' }}>{error}</div>;
  }

  if (items.length === 0) {
    return <div className="text-center p-4" style={{ color: 'var(--text-secondary)' }}>No saved recommendations yet.</div>;
  }

  return (
    <div className="p-4 space-y-3">
      {items.map((item) => (
        <div
          key={item.id}
          className="p-4 rounded-lg cursor-pointer transition-all duration-200"
          style={{
            backgroundColor: selectedId === item.id ? 'var(--card-hover)' : 'var(--card)',
            border: `1px solid ${selectedId === item.id ? 'var(--accent)' : 'var(--border)'}`,
          }}
          onMouseEnter={(e) => {
            if (selectedId !== item.id) {
              e.currentTarget.style.borderColor = 'var(--accent)';
            }
          }}
          onMouseLeave={(e) => {
            if (selectedId !== item.id) {
              e.currentTarget.style.borderColor = 'var(--border)';
            }
          }}
        >
          <div onClick={() => onSelect(item)}>
            <h3 className="font-medium text-sm" style={{ color: 'var(--text)' }}>
              {(() => {
                // Debug: Log the item structure with all available fields
                console.log('=== JOB ITEM DEBUG ===');
                console.log('Label:', item.label);
                console.log('OASIS Code:', item.oasis_code);
                console.log('Description:', item.description);
                console.log('All Fields Keys:', item.all_fields ? Object.keys(item.all_fields) : 'No all_fields');
                console.log('All Fields Full Object:', item.all_fields);
                
                // Log specific searches
                if (item.all_fields) {
                  console.log('Looking for OASIS labels...');
                  Object.keys(item.all_fields || {}).forEach(key => {
                    if (key.toLowerCase().includes('oasis') || key.toLowerCase().includes('label')) {
                      console.log(`  Found: ${key} = ${item.all_fields?.[key]}`);
                    }
                  });
                  
                  console.log('Looking for ESCO titles...');
                  Object.keys(item.all_fields || {}).forEach(key => {
                    if (key.toLowerCase().includes('title') || key.toLowerCase().includes('preferred')) {
                      console.log(`  Found: ${key} = ${item.all_fields?.[key]}`);
                    }
                  });
                }
                console.log('========================');
                
                // Fixed logic based on actual data structure
                if (item.all_fields) {
                  // For OASIS jobs (detected by career_ prefix OR having oasis_label__final_x field)
                  if (item.oasis_code?.startsWith('career_') || item.all_fields.oasis_label__final_x) {
                    console.log('This is an OASIS job');
                    // Use oasis_label__final_x field for OASIS jobs
                    if (item.all_fields.oasis_label__final_x) {
                      console.log(`Using OASIS title: ${item.all_fields.oasis_label__final_x}`);
                      return item.all_fields.oasis_label__final_x;
                    }
                  } 
                  
                  // For ESCO jobs - use job_title_text or other title fields
                  if (item.all_fields.job_title_text) {
                    console.log('This is an ESCO job');
                    console.log(`Using ESCO title: ${item.all_fields.job_title_text}`);
                    // Extract first title from pipe-separated list
                    const titles = item.all_fields.job_title_text.split(' | ');
                    return titles[0];
                  }
                }
                
                console.log('Using fallback label:', item.label);
                return item.label || 'No Title Found';
              })()}
            </h3>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              {item.oasis_code?.startsWith('career_') || item.all_fields?.oasis_label__final_x ? 'OASIS Career' : 
               item.all_fields?.job_title_text ? 'ESCO Career' : item.oasis_code}
            </p>
          </div>
          <button
            onClick={() => onDelete(item)}
            className="mt-2 text-xs font-medium transition-colors duration-200"
            style={{ color: 'var(--text-secondary)' }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
            onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}