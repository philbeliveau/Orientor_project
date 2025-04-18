import React, { useState, useEffect } from 'react';
import { Box, Button, CircularProgress, Typography, Alert } from '@mui/material';
import axios from 'axios';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const REACTIVE_RESUME_URL = process.env.NEXT_PUBLIC_REACTIVE_RESUME_URL || 'http://localhost:3100';

interface Resume {
  id: string;
  name?: string;
}

interface ResumeFrameProps {
  token?: string;
}

const ResumeFrame: React.FC<ResumeFrameProps> = ({ token }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resumeUrl, setResumeUrl] = useState<string | null>(null);
  const [resumeList, setResumeList] = useState<Resume[]>([]);

  useEffect(() => {
    const fetchOrCreateResume = async () => {
      try {
        setLoading(true);
        
        console.log('Fetching with token:', token);
        console.log('Backend URL:', BACKEND_URL);
        console.log('Resume URL:', REACTIVE_RESUME_URL);
        
        if (!token) {
          setError('Authentication required. Please log in.');
          return;
        }

        try {
          // First try to list existing resumes
          const listResponse = await axios.get<{ resumes: Resume[] }>(`${BACKEND_URL}/resume/list`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          
          const resumes = listResponse.data.resumes || [];
          console.log('Fetched resumes:', resumes);
          setResumeList(resumes);
          
          // If resumes exist, use the first one
          if (resumes.length > 0) {
            const resumeId = resumes[0].id;
            setResumeUrl(`${REACTIVE_RESUME_URL}/resume/editor/${resumeId}`);
          } else {
            // Otherwise create a new resume
            const response = await axios.post<{ edit_url: string }>(`${BACKEND_URL}/resume/create`, {}, {
              headers: {
                Authorization: `Bearer ${token}`
              }
            });
            
            if (response.data && response.data.edit_url) {
              setResumeUrl(`${REACTIVE_RESUME_URL}/${response.data.edit_url}`);
            } else {
              throw new Error('Failed to get resume URL');
            }
          }
        } catch (err: any) {
          console.error('Error communicating with backend:', err);
          if (err.response && err.response.status === 404) {
            setError('Resume service is not available. Please make sure Reactive Resume is running.');
          } else {
            // If backend communication fails, try direct access to Reactive Resume
            setResumeUrl(REACTIVE_RESUME_URL);
          }
        }
      } catch (err: any) {
        console.error('Error in fetchOrCreateResume:', err);
        setError(err.message || 'Failed to access resume builder');
      } finally {
        setLoading(false);
      }
    };

    fetchOrCreateResume();
  }, [token]);

  const handleCreateNewResume = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post<{ edit_url: string }>(`${BACKEND_URL}/resume/create`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data && response.data.edit_url) {
        setResumeUrl(`${REACTIVE_RESUME_URL}/${response.data.edit_url}`);
        
        // Refresh the list
        const listResponse = await axios.get<{ resumes: Resume[] }>(`${BACKEND_URL}/resume`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        setResumeList(listResponse.data.resumes || []);
      } else {
        throw new Error('Failed to get resume URL');
      }
    } catch (err: any) {
      console.error('Error creating new resume:', err);
      setError(err.message || 'Failed to create new resume');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectResume = (resumeId: string) => {
    setResumeUrl(`${REACTIVE_RESUME_URL}/resume/editor/${resumeId}`);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%" p={4}>
        <CircularProgress />
        <Typography ml={2}>Loading your resume...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
        <Button variant="contained" color="primary" onClick={() => window.location.reload()} sx={{ mt: 2 }}>
          Try Again
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', width: '100%' }}>
      {resumeList.length > 0 && (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2, p: 2, backgroundColor: '#f5f5f5' }}>
          <Typography variant="subtitle1" sx={{ mr: 2, alignSelf: 'center' }}>
            Your Resumes:
          </Typography>
          
          {resumeList.map((resume) => (
            <Button 
              key={resume.id}
              variant={resumeUrl?.includes(resume.id) ? "contained" : "outlined"} 
              size="small"
              onClick={() => handleSelectResume(resume.id)}
              sx={{ mr: 1 }}
            >
              {resume.name || `Resume ${resume.id.slice(0, 4)}`}
            </Button>
          ))}
          
          <Button 
            variant="outlined" 
            color="primary" 
            size="small"
            onClick={handleCreateNewResume}
          >
            Create New
          </Button>
        </Box>
      )}
      
      {resumeUrl ? (
        <Box sx={{ flexGrow: 1, border: '1px solid #e0e0e0', borderRadius: '4px', overflow: 'hidden', height: 'calc(100% - 60px)' }}>
          <iframe
            src={resumeUrl}
            style={{ 
              width: '100%', 
              height: '100%', 
              border: 'none'
            }}
            title="Resume Editor"
            allowFullScreen
          />
        </Box>
      ) : (
        <Box display="flex" justifyContent="center" alignItems="center" height="100%" p={4}>
          <Button variant="contained" color="primary" onClick={handleCreateNewResume}>
            Create Your First Resume
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ResumeFrame; 