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
                // Debug: Log the item structure
                console.log('Job item data:', {
                  label: item.label,
                  oasis_code: item.oasis_code,
                  all_fields: item.all_fields,
                  description: item.description
                });
                
                // Handle OASIS jobs (occupation::key_ or career_ prefixes)
                if (item.oasis_code?.startsWith('occupation::key_') || item.label?.startsWith('career_')) {
                  // Look for "Oasis Label Final X" pattern in all_fields
                  const allFields = item.all_fields;
                  if (allFields) {
                    // Check for Oasis Label Final X (where X is a number)
                    for (const [key, value] of Object.entries(allFields)) {
                      if (key.match(/^Oasis Label Final \d+$/) && value) {
                        return value as string;
                      }
                    }
                    // Also check for exact "Oasis Label Final X" patterns
                    if (allFields['Oasis Label Final 1']) return allFields['Oasis Label Final 1'];
                    if (allFields['Oasis Label Final 2']) return allFields['Oasis Label Final 2'];
                    if (allFields['Oasis Label Final 3']) return allFields['Oasis Label Final 3'];
                    if (allFields['Oasis Label Final 4']) return allFields['Oasis Label Final 4'];
                    if (allFields['Oasis Label Final 5']) return allFields['Oasis Label Final 5'];
                  }
                  return item.label || 'OASIS Career';
                }
                
                // Handle ESCO jobs - look for title field (case variations)
                const allFields = item.all_fields;
                if (allFields) {
                  // Try different case variations of title
                  if (allFields.title) return allFields.title;
                  if (allFields.Title) return allFields.Title;
                  if (allFields.TITLE) return allFields.TITLE;
                  if (allFields.preferredLabel) return allFields.preferredLabel;
                  if (allFields.PreferredLabel) return allFields.PreferredLabel;
                }
                
                // Fallback to label for other cases
                return item.label || 'Career';
              })()}
            </h3>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              {item.oasis_code?.startsWith('occupation::key_') ? 'OASIS Career' : 
               item.all_fields?.Title ? 'ESCO Career' : item.oasis_code}
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