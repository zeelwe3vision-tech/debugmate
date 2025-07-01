import React from 'react';
import './Dashboard.css';
import { FiUsers } from 'react-icons/fi';
import 'react-circular-progressbar/dist/styles.css';
import { FiMoreHorizontal, FiFilter, FiHeart, FiPlus, FiChevronDown } from 'react-icons/fi';


const ongoingProjectsData = [
    { id: 1, date: 'March 05, 2024', title: 'Web Designing', subtitle: 'Prototyping', progress: 90, daysLeft: 2, team: ['1', '2', '3'], color: 'yellow' },
    { id: 2, date: 'March 08, 2024', title: 'Mobile App', subtitle: 'Design', progress: 50, daysLeft: 6, team: ['4', '5', '6'], color: 'blue' },
    { id: 3, date: 'March 12, 2024', title: 'Dashboard', subtitle: 'Wireframe', progress: 70, daysLeft: 8, team: ['7', '8', '9'], color: 'red' },
];

const StatCard = ({ value, title }) => (
    <div className="stat-card">
        <div className="stat-value">{value}</div>
        <div className="stat-title">{title}</div>
    </div>
);

const ProjectCard = ({ project }) => (
    <div className={`project-card card-${project.color}`}>
        <div className="card-header">
            <span className="date-tag">{project.date}</span>
            <FiMoreHorizontal />
        </div>
        <h4 className="project-title">{project.title}</h4>
        <div className="progress-section">
            <p className="project-subtitle">{project.subtitle}</p>
            <span className="progress-tag">{project.progress}% Progress</span>
        </div>
        <div className="progress-bar-container">
            <div className="progress-bar-fill" style={{ width: `${project.progress}%` }}></div>
        </div>
        <div className="card-footer">
            <div className="team-avatars">
                {project.team.map(imgId => <img key={imgId} src={`https://i.pravatar.cc/24?img=${imgId}`} alt="avatar" />)}
                <button className="add-member-btn"><FiPlus /></button>
            </div>
            <span className="days-left-tag">{project.daysLeft} Days Left</span>
        </div>
    </div>
);

const OngoingProjects = () => (
    <div className="widget ongoing-projects-widget">
        <div className="widget-header">
            <button className="widget-title-btn">Ongoing Projects <FiChevronDown /></button>
            <div className="header-icons">
                <button className="icon-btn"><FiPlus /></button>
                <button className="icon-btn"><FiFilter /></button>
                <button className="icon-btn"><FiHeart /></button>
            </div>
        </div>
        <div className="projects-container">
            {ongoingProjectsData.map(project => <ProjectCard key={project.id} project={project} />)}
        </div>
    </div>
);


const Dashboard = () => {
    return (
        <div className="dashboard-container">
            <div className="dashboard-grid">
                <div className="left-column">
                    <StatCard value="04" title="Open Project" />
                    <StatCard value="02" title="Project Completed" />
                    <StatCard value="08" title="Daily working Hours" />
                    <StatCard value="45.99" title="Total Project Hours" />
                    <div className='right-sidebar'>
                        <div className='widget staff-info'>
                            <div>
                                <FiUsers />
                                <p>20</p>
                                <p>Number of Staff</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="main-content">
                    <OngoingProjects />
                </div>

            </div>
        </div>
    );
};

export default Dashboard; 