// Project Database Service
// This service handles all database operations for project data

class ProjectDatabase {
    constructor() {
        this.storageKey = 'debugmate_projects';
        this.initializeDatabase();
    }

    // Initialize database if empty
    initializeDatabase() {
        if (!localStorage.getItem(this.storageKey)) {
            localStorage.setItem(this.storageKey, JSON.stringify([]));
        }
    }

    // Get all projects
    getAllProjects() {
        try {
            const projects = localStorage.getItem(this.storageKey);
            return projects ? JSON.parse(projects) : [];
        } catch (error) {
            console.error('Error retrieving projects:', error);
            return [];
        }
    }

    // Get project by ID
    getProjectById(id) {
        const projects = this.getAllProjects();
        return projects.find(project => project.id === id);
    }

    // Save new project
    saveProject(projectData) {
        try {
            const projects = this.getAllProjects();
            const newProject = {
                ...projectData,
                id: this.generateId(),
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            projects.push(newProject);
            localStorage.setItem(this.storageKey, JSON.stringify(projects));
            return {
                success: true,
                project: newProject,
                message: 'Project saved successfully!'
            };
        } catch (error) {
            console.error('Error saving project:', error);
            return {
                success: false,
                message: 'Failed to save project. Please try again.'
            };
        }
    }

    // Update existing project
    updateProject(id, updatedData) {
        try {
            const projects = this.getAllProjects();
            const projectIndex = projects.findIndex(project => project.id === id);
            
            if (projectIndex === -1) {
                return {
                    success: false,
                    message: 'Project not found'
                };
            }

            projects[projectIndex] = {
                ...projects[projectIndex],
                ...updatedData,
                updatedAt: new Date().toISOString()
            };

            localStorage.setItem(this.storageKey, JSON.stringify(projects));
            
            return {
                success: true,
                project: projects[projectIndex],
                message: 'Project updated successfully!'
            };
        } catch (error) {
            console.error('Error updating project:', error);
            return {
                success: false,
                message: 'Failed to update project. Please try again.'
            };
        }
    }

    // Delete project
    deleteProject(id) {
        try {
            const projects = this.getAllProjects();
            const filteredProjects = projects.filter(project => project.id !== id);
            
            if (filteredProjects.length === projects.length) {
                return {
                    success: false,
                    message: 'Project not found'
                };
            }

            localStorage.setItem(this.storageKey, JSON.stringify(filteredProjects));
            
            return {
                success: true,
                message: 'Project deleted successfully!'
            };
        } catch (error) {
            console.error('Error deleting project:', error);
            return {
                success: false,
                message: 'Failed to delete project. Please try again.'
            };
        }
    }

    // Generate unique ID
    generateId() {
        const projects = this.getAllProjects();
        const maxId = projects.length > 0 ? Math.max(...projects.map(p => p.id)) : 0;
        return maxId + 1;
    }

    // Search projects
    searchProjects(query) {
        const projects = this.getAllProjects();
        const searchTerm = query.toLowerCase();
        
        return projects.filter(project => 
            project.projectName.toLowerCase().includes(searchTerm) ||
            project.projectDescription.toLowerCase().includes(searchTerm) ||
            project.clientName.toLowerCase().includes(searchTerm) ||
            project.techStack.some(tech => tech.toLowerCase().includes(searchTerm))
        );
    }

    // Get projects by status
    getProjectsByStatus(status) {
        const projects = this.getAllProjects();
        return projects.filter(project => project.status === status);
    }

    // Get projects by date range
    getProjectsByDateRange(startDate, endDate) {
        const projects = this.getAllProjects();
        return projects.filter(project => 
            project.startDate >= startDate && project.endDate <= endDate
        );
    }

    // Export data
    exportData() {
        const projects = this.getAllProjects();
        const dataStr = JSON.stringify(projects, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `debugmate_projects_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
    }

    // Import data
    importData(jsonData) {
        try {
            const projects = JSON.parse(jsonData);
            if (Array.isArray(projects)) {
                localStorage.setItem(this.storageKey, JSON.stringify(projects));
                return {
                    success: true,
                    message: `Successfully imported ${projects.length} projects`
                };
            } else {
                return {
                    success: false,
                    message: 'Invalid data format'
                };
            }
        } catch (error) {
            return {
                success: false,
                message: 'Failed to parse JSON data'
            };
        }
    }

    // Clear all data
    clearAllData() {
        localStorage.removeItem(this.storageKey);
        this.initializeDatabase();
    }
}

// Create and export a singleton instance
const projectDatabase = new ProjectDatabase();
export default projectDatabase; 