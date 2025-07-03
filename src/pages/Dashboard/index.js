import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { FiUsers, FiMoreHorizontal, FiFilter, FiHeart, FiPlus,} from 'react-icons/fi';
import './Dashboard.css';
import { Link } from 'react-router-dom';

const ongoingProjectsData = [
  { id: 1, date: 'March 05, 2024', title: 'Web Designing', subtitle: 'Prototyping', progress: 90, daysLeft: 2, team: ['1', '2', '3'], color: 'yellow' },
  { id: 2, date: 'March 08, 2024', title: 'Mobile App', subtitle: 'Design', progress: 50, daysLeft: 6, team: ['4', '5', '6'], color: 'blue' },
  { id: 3, date: 'March 12, 2024', title: 'Dashboard', subtitle: 'Wireframe', progress: 70, daysLeft: 8, team: ['7', '8', '9'], color: 'red' },
];

const StatCard = ({ value, title, icon }) => (
  <div className="stat-card-custom d-flex flex-column align-items-center justify-content-center">
    {icon && <div className="mb-2">{icon}</div>}
    <div className="stat-value">{value}</div>
    <div className="stat-title">{title}</div>
  </div>
);

const ProjectCard = ({ project }) => (
  <div className={`project-card-custom card-${project.color}`}>
    <div className="d-flex justify-content-between align-items-center mb-2">
      <span className="date-tag">{project.date}</span>
      <FiMoreHorizontal />
    </div>
    <h4 className="project-title">{project.title}</h4>
    <div className="d-flex justify-content-between align-items-center mb-2">
      <p className="project-subtitle mb-0">{project.subtitle}</p>
    </div>
    <div className="d-flex justify-content-between align-items-center mt-2">
      <div className=" d-flex align-items-center ">
        <Link to="/chatbot/DualChatbot" className="btn chat">Create New Chat With Chatbot</Link>
      </div>
    </div>
  </div>
);
const Dashboard = () => (
  <Container fluid className="dashboard-container">
    <Row className="g-4 mb-4 justify-content-center">
      <Col md={2} sm={6} xs={12}><StatCard value="04" title="Open Project" /></Col>
      <Col md={2} sm={6} xs={12}><StatCard value="02" title="Project Completed" /></Col>
      <Col md={2} sm={6} xs={12}><StatCard value="08" title="Daily working Hours" /></Col>
      <Col md={2} sm={6} xs={12}><StatCard value="45.99" title="Total Project Hours" /></Col>
      <Col md={2} sm={6} xs={12}><StatCard value={<><FiUsers size={32} /><div>20</div></>} title="Number of Staff" /></Col>
    </Row>
    <Row>
      <Col>
        <div className="widget-custom ongoing-projects-widget-custom">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <Button className="widget-title-btn me-3">Ongoing Projects</Button>
            <div className="header-icons d-flex gap-2">
              <Button className="icon-btn"><FiPlus /></Button>
              <Button className="icon-btn"><FiFilter /></Button>
              <Button className="icon-btn"><FiHeart /></Button>
            </div> 
          </div>
          <div className="d-flex flex-row flex-nowrap overflow-auto gap-3 projects-container-custom">
            {ongoingProjectsData.map(project => (
              <div key={project.id} style={{ minWidth: 240, maxWidth: 360 }}>
                <ProjectCard project={project} />
              </div>
            ))}
          </div>
        </div>
      </Col>
    </Row>
  </Container>
);

export default Dashboard;