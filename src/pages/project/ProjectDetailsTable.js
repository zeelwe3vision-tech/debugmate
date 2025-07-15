import React, { useEffect, useState } from 'react';
import projectDatabaseSupabase from '../../services/projectDatabaseSupabase';
import { Table, Button, Card, Row, Col, ToggleButtonGroup, ToggleButton, Spinner, Alert } from 'react-bootstrap';
import './projectDetailsTable.css'

const ProjectDetailsTable = () => {
  const [projects, setProjects] = useState([]);
  const [view, setView] = useState('table');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const projectsData = await projectDatabaseSupabase.getAllProjects();
      setProjects(projectsData);
      setError(null);
    } catch (err) {
      console.error('Error loading projects:', err);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      const result = await projectDatabaseSupabase.deleteProject(id);
      if (result.success) {
        await loadProjects(); // Reload the projects
      } else {
        setError('Failed to delete project. Please try again.');
      }
    } catch (err) {
      console.error('Error deleting project:', err);
      setError('Failed to delete project. Please try again.');
    }
  };

  return (
    <div className='table_container'>
      <h2 className='d-flex align-items-center justify-content-center mb-4'>Project Details</h2>
      
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      <div className='d-flex justify-content-center mb-3'>
        <ToggleButtonGroup type="radio" name="view" value={view} onChange={setView}>
          <ToggleButton id="tbg-radio-1" value={'table'} variant={view === 'table' ? 'primary' : 'outline-primary'}>Table View</ToggleButton>
          <ToggleButton id="tbg-radio-2" value={'card'} variant={view === 'card' ? 'primary' : 'outline-primary'}>Card View</ToggleButton>
        </ToggleButtonGroup>
      </div>
      
      {loading ? (
        <div className='d-flex justify-content-center'>
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      ) : (
        <>
          {view === 'table' ? (
            <Table className='align-items-center justify-content-center' striped bordered hover responsive>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Project Name</th>
                  <th>Description</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Status</th>
                  <th>Team Members</th>
                  <th>Client Name</th>
                  <th>Tech Stack</th>
                  <th>Leader</th>
                  <th>Documents</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {projects.length === 0 ? (
                  <tr><td colSpan={12} className="text-center">No projects found.</td></tr>
                ) : (
                  projects.map((proj, idx) => (
                    <tr key={proj.id}>
                      <td>{idx + 1}</td>
                      <td>{proj.name || proj.projectName}</td>
                      <td>{proj.description || proj.projectDescription}</td>
                      <td>{proj.start_date || proj.startDate}</td>
                      <td>{proj.end_date || proj.endDate}</td>
                      <td>{proj.status}</td>
                      <td>{(proj.assigned_to || proj.assignedTo || []).join(', ')}</td>
                      <td>{proj.client_name || proj.clientName}</td>
                      <td>{(proj.tech_stack || proj.techStack || []).join(', ')}</td>
                      <td>{proj.leader_of_project || proj.leaderOfProject}</td>
                      <td>
                        {Array.isArray(proj.upload_documents || proj.uploadDocuments) && (proj.upload_documents || proj.uploadDocuments).length > 0 ? (
                          (proj.upload_documents || proj.uploadDocuments).map((file, i) => (
                            <div key={i}>
                              <a href={file.data} download={file.name} style={{ color: '#007bff', textDecoration: 'underline' }}>
                                {file.name}
                              </a>
                            </div>
                          ))
                        ) : (
                          <span style={{ color: '#888' }}>No files</span>
                        )}
                      </td>
                      <td>
                        <Button variant="danger" size="sm" onClick={() => handleDelete(proj.id)}>Delete</Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </Table>
          ) : (
            <Row xs={1} md={2} lg={3} className="g-4">
              {projects.length === 0 ? (
                <Col><div className="text-center">No projects found.</div></Col>
              ) : (
                projects.map((proj, idx) => (
                  <Col key={proj.id}>
                    <Card className="mb-3">
                      <Card.Body>
                        <Card.Title>{proj.name || proj.projectName}</Card.Title>
                        <Card.Subtitle className="mb-2 text-muted">{proj.status}</Card.Subtitle>
                        <Card.Text>
                          <strong>Description:</strong> {proj.description || proj.projectDescription}<br/>
                          <strong>Start Date:</strong> {proj.start_date || proj.startDate}<br/>
                          <strong>End Date:</strong> {proj.end_date || proj.endDate}<br/>
                          <strong>Team Members:</strong> {(proj.assigned_to || proj.assignedTo || []).join(', ')}<br/>
                          <strong>Client Name:</strong> {proj.client_name || proj.clientName}<br/>
                          <strong>Tech Stack:</strong> {(proj.tech_stack || proj.techStack || []).join(', ')}<br/>
                          <strong>Leader:</strong> {proj.leader_of_project || proj.leaderOfProject}<br/>
                          <strong>Documents:</strong> {Array.isArray(proj.upload_documents || proj.uploadDocuments) && (proj.upload_documents || proj.uploadDocuments).length > 0 ? (
                            (proj.upload_documents || proj.uploadDocuments).map((file, i) => (
                              <div key={i}>
                                <a href={file.data} download={file.name} style={{ color: '#007bff', textDecoration: 'underline' }}>
                                  {file.name}
                                </a>
                              </div>
                            ))
                          ) : (
                            <span style={{ color: '#888' }}>No files</span>
                          )}
                        </Card.Text>
                        <Button variant="danger" size="sm" onClick={() => handleDelete(proj.id)}>Delete</Button>
                      </Card.Body>
                    </Card>
                  </Col>
                ))
              )}
            </Row>
          )}
        </>
      )}
    </div>
  );
};

export default ProjectDetailsTable;