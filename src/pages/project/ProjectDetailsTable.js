import React, { useEffect, useState } from 'react';
import projectDatabase from '../../services/projectDatabase';
import { Table, Button } from 'react-bootstrap';
import './projectDetailsTable.css'

const ProjectDetailsTable = () => {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    setProjects(projectDatabase.getAllProjects());
  }, []);

  const handleDelete = (id) => {
    projectDatabase.deleteProject(id);
    setProjects(projectDatabase.getAllProjects());
  };

  return (
    <div className='table_container' >
      <h2 className='d-flex align-items-center justify-content-center mb-4'>Project Details</h2>
      <Table className=' align-items-center justify-content-center' striped bordered hover responsive>
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
    </div>
  );
};

export default ProjectDetailsTable; 