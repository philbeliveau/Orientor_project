import React, { useState } from 'react';
import { Note } from '@/services/spaceService';
import { createNote, updateNote, deleteNote } from '@/services/spaceService';

interface NotesSectionProps {
  recommendation: {
    id: number;
    notes?: Note[];
  };
}

const NotesSection: React.FC<NotesSectionProps> = ({ recommendation }) => {
  const [notes, setNotes] = useState<Note[]>(recommendation.notes || []);
  const [newNote, setNewNote] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState('');

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    
    try {
      const createdNote = await createNote({
        content: newNote,
        saved_recommendation_id: recommendation.id
      });
      
      setNotes([...notes, createdNote]);
      setNewNote('');
    } catch (error) {
      console.error('Error creating note:', error);
    }
  };

  const handleEditNote = async (noteId: number) => {
    if (!editingContent.trim()) return;
    
    try {
      const updatedNote = await updateNote(noteId, {
        content: editingContent
      });
      
      setNotes(notes.map(note => 
        note.id === noteId ? updatedNote : note
      ));
      
      setEditingNoteId(null);
      setEditingContent('');
    } catch (error) {
      console.error('Error updating note:', error);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    try {
      await deleteNote(noteId);
      setNotes(notes.filter(note => note.id !== noteId));
    } catch (error) {
      console.error('Error deleting note:', error);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Notes</h2>
      
      {/* Add new note */}
      <div className="mb-6">
        <textarea
          className="w-full p-3 rounded-lg bg-neutral-800/50 border border-neutral-700/30 focus:border-primary-teal/50 focus:ring-1 focus:ring-primary-teal/50"
          rows={3}
          placeholder="Add a note..."
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
        />
        <button
          className="mt-2 px-4 py-2 bg-primary-teal/20 text-primary-teal rounded-lg hover:bg-primary-teal/30 transition-colors"
          onClick={handleAddNote}
        >
          Add Note
        </button>
      </div>
      
      {/* Notes list */}
      <div className="space-y-4">
        {notes.map(note => (
          <div key={note.id} className="p-4 rounded-lg bg-neutral-800/50 border border-neutral-700/30">
            {editingNoteId === note.id ? (
              <div>
                <textarea
                  className="w-full p-3 rounded-lg bg-neutral-800/50 border border-neutral-700/30 focus:border-primary-teal/50 focus:ring-1 focus:ring-primary-teal/50"
                  rows={3}
                  value={editingContent}
                  onChange={(e) => setEditingContent(e.target.value)}
                />
                <div className="mt-2 space-x-2">
                  <button
                    className="px-3 py-1 bg-primary-teal/20 text-primary-teal rounded-lg hover:bg-primary-teal/30 transition-colors"
                    onClick={() => handleEditNote(note.id)}
                  >
                    Save
                  </button>
                  <button
                    className="px-3 py-1 bg-neutral-700/50 text-neutral-300 rounded-lg hover:bg-neutral-700/70 transition-colors"
                    onClick={() => {
                      setEditingNoteId(null);
                      setEditingContent('');
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <p className="text-neutral-300">{note.content}</p>
                <div className="mt-2 text-sm text-neutral-500">
                  {new Date(note.created_at).toLocaleDateString()}
                </div>
                <div className="mt-2 space-x-2">
                  <button
                    className="px-3 py-1 bg-neutral-700/50 text-neutral-300 rounded-lg hover:bg-neutral-700/70 transition-colors"
                    onClick={() => {
                      setEditingNoteId(note.id);
                      setEditingContent(note.content);
                    }}
                  >
                    Edit
                  </button>
                  <button
                    className="px-3 py-1 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                    onClick={() => handleDeleteNote(note.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default NotesSection; 