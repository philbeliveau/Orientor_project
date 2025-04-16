import React, { useState, useEffect } from 'react';
import { fetchNotes, createNote, updateNote, deleteNote } from '@/services/spaceService';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface Note {
  id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

interface NotesSectionProps {
  recommendationId: number;
}

const NotesSection: React.FC<NotesSectionProps> = ({ recommendationId }) => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadNotes();
  }, [recommendationId]);

  const loadNotes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchNotes(recommendationId);
      setNotes(data);
    } catch (err) {
      console.error('Error loading notes:', err);
      setError('Failed to load notes. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitNewNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteContent.trim()) return;
    
    try {
      const newNote = await createNote({
        content: newNoteContent,
        saved_recommendation_id: recommendationId
      });
      
      setNotes([...notes, newNote]);
      setNewNoteContent('');
    } catch (err) {
      console.error('Error creating note:', err);
      setError('Failed to create note. Please try again.');
    }
  };

  const handleStartEdit = (note: Note) => {
    setEditingNoteId(note.id);
    setEditContent(note.content);
  };

  const handleCancelEdit = () => {
    setEditingNoteId(null);
    setEditContent('');
  };

  const handleSaveEdit = async (noteId: number) => {
    if (!editContent.trim()) return;
    
    try {
      const updatedNote = await updateNote(noteId, { content: editContent });
      setNotes(notes.map(note => note.id === noteId ? updatedNote : note));
      setEditingNoteId(null);
    } catch (err) {
      console.error('Error updating note:', err);
      setError('Failed to update note. Please try again.');
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    try {
      await deleteNote(noteId);
      setNotes(notes.filter(note => note.id !== noteId));
    } catch (err) {
      console.error('Error deleting note:', err);
      setError('Failed to delete note. Please try again.');
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Notes</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-300">
          {error}
        </div>
      )}
      
      {isLoading ? (
        <div className="flex justify-center py-8">
          <LoadingSpinner size="md" />
        </div>
      ) : (
        <>
          <div className="space-y-4 mb-6">
            {notes.length === 0 ? (
              <p className="text-neutral-400 text-center py-4">
                No notes yet. Add one below to track your thoughts.
              </p>
            ) : (
              notes.map(note => (
                <div key={note.id} className="bg-neutral-800/60 rounded-lg p-4 border border-neutral-700/30">
                  {editingNoteId === note.id ? (
                    <div className="space-y-3">
                      <textarea
                        className="input w-full h-24"
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                      />
                      <div className="flex justify-end space-x-2">
                        <button
                          className="btn btn-sm btn-ghost"
                          onClick={handleCancelEdit}
                        >
                          Cancel
                        </button>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => handleSaveEdit(note.id)}
                        >
                          Save
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <p className="text-neutral-100 whitespace-pre-wrap">{note.content}</p>
                      <div className="flex justify-between items-center mt-3">
                        <span className="text-sm text-neutral-400">
                          {formatDate(note.updated_at || note.created_at)}
                        </span>
                        <div className="flex space-x-2">
                          <button
                            className="text-neutral-400 hover:text-neutral-200"
                            onClick={() => handleStartEdit(note)}
                          >
                            Edit
                          </button>
                          <button
                            className="text-neutral-400 hover:text-red-400"
                            onClick={() => handleDeleteNote(note.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>

          <form onSubmit={handleSubmitNewNote}>
            <div className="space-y-3">
              <textarea
                className="input w-full h-24"
                placeholder="Add a new note..."
                value={newNoteContent}
                onChange={(e) => setNewNoteContent(e.target.value)}
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!newNoteContent.trim()}
                >
                  Add Note
                </button>
              </div>
            </div>
          </form>
        </>
      )}
    </div>
  );
};

export default NotesSection; 