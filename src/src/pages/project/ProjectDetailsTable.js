import React, { useEffect, useState } from 'react';
import projectDatabase from '../../services/projectDatabase';
import { Table, Button, Card, Row, Col, ToggleButtonGroup, ToggleButton } from 'react-bootstrap';
import './projectDetailsTable.css'

const ProjectDetailsTable = () => {
  const [projects, setProjects] = useState([]);
  const [view, setView] = useState('table');

  useEffect(() => {
    setProjects(projectDatabase.getAllProjects());
  }, []);

  const handleDelete = (id) => {
    projectDatabase.deleteProject(id);
    setProjects(projectDatabase.getAllProjects());
  };

  return (
    <div className='table_container'>
      <h2 className='d-flex align-items-center justify-content-center mb-4'>Project Details</h2>
      <div className='d-flex justify-content-center mb-3'>
        <ToggleButtonGroup type="radio" name="view" value={view} onChange={setView}>
          <ToggleButton id="tbg-radio-1" value={'table'} variant={view === 'table' ? 'primary' : 'outline-primary'}>Table View</ToggleButton>
          <ToggleButton id="tbg-radio-2" value={'card'} variant={view === 'card' ? 'primary' : 'outline-primary'}>Card View</ToggleButton>
        </ToggleButtonGroup>
      </div>
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
                  <td>{proj.projectName}</td>
                  <td>{proj.projectDescription}</td>
                  <td>{proj.startDate}</td>
                  <td>{proj.endDate}</td>
                  <td>{proj.status}</td>
                  <td>{(proj.assignedTo || []).join(', ')}</td>
                  <td>{proj.clientName}</td>
                  <td>{(proj.techStack || []).join(', ')}</td>
                  <td>{proj.leaderOfProject}</td>
                  <td>
                    {Array.isArray(proj.uploadDocuments) && proj.uploadDocuments.length > 0 ? (
                      proj.uploadDocuments.map((file, i) => (
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
                    <Card.Title>{proj.projectName}</Card.Title>
                    <Card.Subtitle className="mb-2 text-muted">{proj.status}</Card.Subtitle>
                    <Card.Text>
                      <strong>Description:</strong> {proj.projectDescription}<br/>
                      <strong>Start Date:</strong> {proj.startDate}<br/>
                      <strong>End Date:</strong> {proj.endDate}<br/>
                      <strong>Team Members:</strong> {(proj.assignedTo || []).join(', ')}<br/>
                      <strong>Client Name:</strong> {proj.clientName}<br/>
                      <strong>Tech Stack:</strong> {(proj.techStack || []).join(', ')}<br/>
                      <strong>Leader:</strong> {proj.leaderOfProject}<br/>
                      <strong>Documents:</strong> {Array.isArray(proj.uploadDocuments) && proj.uploadDocuments.length > 0 ? (
                        proj.uploadDocuments.map((file, i) => (
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
    </div>
  );
};

export default ProjectDetailsTable; 