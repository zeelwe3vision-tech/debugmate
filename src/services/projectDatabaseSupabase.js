// Project Database Service with Supabase
// This service handles all database operations for project data using Supabase

import { databaseService } from './supabase';

class ProjectDatabaseSupabase {
    constructor() {
        this.storageKey = 'debugmate_projects';
        // Keep localStorage as fallback for offline functionality
        this.initializeLocalStorage();
    }

    // Initialize local storage if empty (for offline fallback)
    initializeLocalStorage() {
        if (!localStorage.getItem(this.storageKey)) {
            localStorage.setItem(this.storageKey, JSON.stringify([]));
        }
    }

    // Get all projects from Supabase
    async getAllProjects() {
        try {
            const { data, error } = await databaseService.getProjects();
            if (error) {
                console.error('Error fetching projects from Supabase:', error);
                // Fallback to localStorage
                return this.getLocalProjects();
            }
            return data || [];
        } catch (error) {
            console.error('Error in getAllProjects:', error);
            // Fallback to localStorage
            return this.getLocalProjects();
        }
    }

    // Get local projects (fallback)
    getLocalProjects() {
        try {
            const projects = localStorage.getItem(this.storageKey);
            return projects ? JSON.parse(projects) : [];
        } catch (error) {
            console.error('Error retrieving local projects:', error);
            return [];
        }
    }

    // Get project by ID
    async getProjectById(id) {
        try {
            const { data, error } = await databaseService.getProjectById(id);
            if (error) {
                console.error('Error fetching project from Supabase:', error);
                // Fallback to localStorage
                const localProjects = this.getLocalProjects();
                return localProjects.find(project => project.id === id);
            }
            return data;
        } catch (error) {
            console.error('Error in getProjectById:', error);
            // Fallback to localStorage
            const localProjects = this.getLocalProjects();
            return localProjects.find(project => project.id === id);
        }
    }

    // Save new project
    async saveProject(projectData) {
        try {
            const projectToSave = {
                project_name: projectData.projectName,
                project_description: projectData.projectDescription,
                start_date: projectData.startDate,
                end_date: projectData.endDate,
                status: projectData.status,
                assigned_role: projectData.assignedRole,
                assigned_to: projectData.assignedTo,
                priority: projectData.priority,
                client_name: projectData.clientName,
                upload_documents: projectData.uploadDocuments,
                project_scope: projectData.projectScope,
                tech_stack: projectData.techStack,
                tech_stack_custom: projectData.techStackCustom,
                leader_of_project: projectData.leaderOfProject,
                project_responsibility: projectData.projectResponsibility,
                role: projectData.role,
                role_answers: projectData.roleAnswers,
                custom_questions: projectData.customQuestionsList,
                custom_answers: projectData.customAnswers,
            };

            const { data, error } = await databaseService.createProject(projectToSave);
            
            if (error) {
                console.error('Error saving project to Supabase:', error);
                // Fallback to localStorage
                return this.saveProjectLocal(projectData);
            }

            // Also save to localStorage for offline access
            this.saveProjectLocal(projectData);

            return {
                success: true,
                project: data[0],
                message: 'Project saved successfully!'
            };
        } catch (error) {
            console.error('Error in saveProject:', error);
            // Fallback to localStorage
            return this.saveProjectLocal(projectData);
        }
    }

    // Save project to localStorage (fallback)
    saveProjectLocal(projectData) {
        try {
            const projects = this.getLocalProjects();
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
                message: 'Project saved locally!'
            };
        } catch (error) {
            console.error('Error saving project locally:', error);
            return {
                success: false,
                message: 'Failed to save project. Please try again.'
            };
        }
    }

    // Update existing project
    async updateProject(id, updatedData) {
        try {
            const updateData = {
                name: updatedData.projectName,
                description: updatedData.projectDescription,
                client_name: updatedData.clientName,
                tech_stack: updatedData.techStack,
                status: updatedData.status,
                start_date: updatedData.startDate,
                end_date: updatedData.endDate,
            };

            const { data, error } = await databaseService.updateProject(id, updateData);
            
            if (error) {
                console.error('Error updating project in Supabase:', error);
                // Fallback to localStorage
                return this.updateProjectLocal(id, updatedData);
            }

            // Also update localStorage
            this.updateProjectLocal(id, updatedData);

            return {
                success: true,
                project: data[0],
                message: 'Project updated successfully!'
            };
        } catch (error) {
            console.error('Error in updateProject:', error);
            // Fallback to localStorage
            return this.updateProjectLocal(id, updatedData);
        }
    }

    // Update project in localStorage (fallback)
    updateProjectLocal(id, updatedData) {
        try {
            const projects = this.getLocalProjects();
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
                message: 'Project updated locally!'
            };
        } catch (error) {
            console.error('Error updating project locally:', error);
            return {
                success: false,
                message: 'Failed to update project. Please try again.'
            };
        }
    }

    // Delete project
    async deleteProject(id) {
        try {
            const { error } = await databaseService.deleteProject(id);
            
            if (error) {
                console.error('Error deleting project from Supabase:', error);
                // Fallback to localStorage
                return this.deleteProjectLocal(id);
            }

            // Also delete from localStorage
            this.deleteProjectLocal(id);
            
            return {
                success: true,
                message: 'Project deleted successfully!'
            };
        } catch (error) {
            console.error('Error in deleteProject:', error);
            // Fallback to localStorage
            return this.deleteProjectLocal(id);
        }
    }

    // Delete project from localStorage (fallback)
    deleteProjectLocal(id) {
        try {
            const projects = this.getLocalProjects();
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
                message: 'Project deleted locally!'
            };
        } catch (error) {
            console.error('Error deleting project locally:', error);
            return {
                success: false,
                message: 'Failed to delete project. Please try again.'
            };
        }
    }

    // Generate unique ID (for localStorage fallback)
    generateId() {
        const projects = this.getLocalProjects();
        const maxId = projects.length > 0 ? Math.max(...projects.map(p => p.id)) : 0;
        return maxId + 1;
    }

    // Search projects
    async searchProjects(query) {
        try {
            const projects = await this.getAllProjects();
            const searchTerm = query.toLowerCase();
            
            return projects.filter(project => 
                project.name?.toLowerCase().includes(searchTerm) ||
                project.description?.toLowerCase().includes(searchTerm) ||
                project.client_name?.toLowerCase().includes(searchTerm) ||
                project.tech_stack?.some(tech => tech.toLowerCase().includes(searchTerm))
            );
        } catch (error) {
            console.error('Error in searchProjects:', error);
            // Fallback to localStorage
            const localProjects = this.getLocalProjects();
            const searchTerm = query.toLowerCase();
            
            return localProjects.filter(project => 
                project.projectName?.toLowerCase().includes(searchTerm) ||
                project.projectDescription?.toLowerCase().includes(searchTerm) ||
                project.clientName?.toLowerCase().includes(searchTerm) ||
                project.techStack?.some(tech => tech.toLowerCase().includes(searchTerm))
            );
        }
    }

    // Get projects by status
    async getProjectsByStatus(status) {
        try {
            const projects = await this.getAllProjects();
            return projects.filter(project => project.status === status);
        } catch (error) {
            console.error('Error in getProjectsByStatus:', error);
            // Fallback to localStorage
            const localProjects = this.getLocalProjects();
            return localProjects.filter(project => project.status === status);
        }
    }

    // Get projects by date range
    async getProjectsByDateRange(startDate, endDate) {
        try {
            const projects = await this.getAllProjects();
            return projects.filter(project => 
                project.start_date >= startDate && project.end_date <= endDate
            );
        } catch (error) {
            console.error('Error in getProjectsByDateRange:', error);
            // Fallback to localStorage
            const localProjects = this.getLocalProjects();
            return localProjects.filter(project => 
                project.startDate >= startDate && project.endDate <= endDate
            );
        }
    }

    // Export data
    async exportData() {
        try {
            const projects = await this.getAllProjects();
            const dataStr = JSON.stringify(projects, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `debugmate_projects_${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error in exportData:', error);
            // Fallback to localStorage
            const localProjects = this.getLocalProjects();
            const dataStr = JSON.stringify(localProjects, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `debugmate_projects_local_${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            
            URL.revokeObjectURL(url);
        }
    }

    // Import data
    async importData(jsonData) {
        try {
            const projects = JSON.parse(jsonData);
            if (Array.isArray(projects)) {
                // Import to Supabase
                for (const project of projects) {
                    await this.saveProject(project);
                }
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
            console.error('Error in importData:', error);
            return {
                success: false,
                message: 'Failed to parse JSON data'
            };
        }
    }

    // Clear all data
    async clearAllData() {
        try {
            // Clear from Supabase (this would need a bulk delete function)
            // For now, just clear localStorage
            localStorage.removeItem(this.storageKey);
            this.initializeLocalStorage();
            return {
                success: true,
                message: 'Local data cleared successfully'
            };
        } catch (error) {
            console.error('Error in clearAllData:', error);
            return {
                success: false,
                message: 'Failed to clear data'
            };
        }
    }
}

// Create and export a singleton instance
const projectDatabaseSupabase = new ProjectDatabaseSupabase();
export default projectDatabaseSupabase; 