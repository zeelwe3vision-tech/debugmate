import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://nadxrexpfcpnocnsjjbk.supabase.co'
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHhyZXhwZmNwbm9jbnNqamJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjAwNzMsImV4cCI6MjA2NzAzNjA3M30.5T0hxDZabIJ_mTrtKpra3beb7OwnnvpNcUpuAhd28Mw'

// Only create the client if we have valid credentials
let supabase = null;

try {
  if (supabaseUrl && supabaseAnonKey) {
    supabase = createClient(supabaseUrl, supabaseAnonKey)
  } else {
    console.warn('Supabase credentials not configured. Using localStorage fallback only.');
  }
} catch (error) {
  console.error('Error creating Supabase client:', error);
}

export { supabase };

// Database service functions
export const databaseService = {
  // User management
  async signUp(email, password) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    return { data, error }
  },

  async signIn(email, password) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { data, error }
  },

  async signOut() {
    if (!supabase) {
      return { error: { message: 'Supabase not configured' } }
    }
    const { error } = await supabase.auth.signOut()
    return { error }
  },

  async getCurrentUser() {
    if (!supabase) {
      return null
    }
    const { data: { user } } = await supabase.auth.getUser()
    return user
  },

  // Project management
  async getProjects() {
    if (!supabase) {
      return { data: [], error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase
      .from('projects')
      .select('*')
    return { data, error }
  },

  async getProjectById(id) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('id', id)
      .single()
    return { data, error }
  },

  async createProject(projectData) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase
      .from('projects')
      .insert([projectData])
      .select()
    return { data, error }
  },

  async updateProject(id, updates) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase
      .from('projects')
      .update(updates)
      .eq('id', id)
      .select()
    return { data, error }
  },

  async deleteProject(id) {
    if (!supabase) {
      return { error: { message: 'Supabase not configured' } }
    }
    const { error } = await supabase
      .from('projects')
      .delete()
      .eq('id', id)
    return { error }
  },

  // Role management
  async getRoles() {
    const { data, error } = await supabase
      .from('roles')
      .select('*')
    return { data, error }
  },

  async createRole(roleData) {
    const { data, error } = await supabase
      .from('roles')
      .insert([roleData])
      .select()
    return { data, error }
  },

  // Announcements
  async getAnnouncements() {
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
      .order('created_at', { ascending: false })
    return { data, error }
  },

  async createAnnouncement(announcementData) {
    const { data, error } = await supabase
      .from('announcements')
      .insert([announcementData])
      .select()
    return { data, error }
  },

  // API Management
  async getApis() {
    const { data, error } = await supabase
      .from('apis')
      .select('*')
    return { data, error }
  },

  async createApi(apiData) {
    const { data, error } = await supabase
      .from('apis')
      .insert([apiData])
      .select()
    return { data, error }
  },

  // Chatbot messages
  async saveChatMessage(messageData) {
    const { data, error } = await supabase
      .from('chat_messages')
      .insert([messageData])
      .select()
    return { data, error }
  },

  async getChatHistory(userId) {
    const { data, error } = await supabase
      .from('chat_messages')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: true })
    return { data, error }
  },

  // User logins
  async createUserLogin(userLoginData) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase
      .from('user_perms')
      .insert([userLoginData])
      .select()
    return { data, error }
  },

  // Fetch all user logins
  async getAllUserLogins() {
    if (!supabase) {
      return { data: [], error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase
      .from('user_perms')
      .select('*')
    return { data, error }
  },

  // Delete user login by email
  async deleteUserLoginByEmail(email) {
    if (!supabase) {
      return { error: { message: 'Supabase not configured' } }
    }
    const { error } = await supabase
      .from('user_perms')
      .delete()
      .eq('email', email)
    return { error }
  },

  // Update user login by email
  async updateUserLoginByEmail(email, updates) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase
      .from('user_perms')
      .update(updates)
      .eq('email', email)
      .select()
    return { data, error }
  },

  // Get user by email from user_perms
  async getUserByEmail(email) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const { data, error } = await supabase
      .from('user_perms')
      .select('*')
      .eq('email', email)
      .single();
    return { data, error };
  },

  // Helper to get current IST time in ISO format
  getISTISOString() {
    const now = new Date();
    const istOffset = 330; // IST is UTC+5:30 in minutes
    const istTime = new Date(now.getTime() + (istOffset * 60000));
    // Format as ISO string with +05:30
    return istTime.toISOString().replace('Z', '+05:30');
  },

  // Log employee login event
  async logEmployeeLogin({ email, name, password }) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    const login_time = this.getISTISOString();
    const { data, error } = await supabase
      .from('employee_login')
      .insert([{ email, name, pass: password, login_time, logout_time: null }])
      .select();
    return { data, error };
  },

  // Log employee logout event (update the latest login row with logout_time)
  async logEmployeeLogout({ email }) {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } }
    }
    // Find the latest login row for this email with null logout_time
    const { data: latest, error: fetchError } = await supabase
      .from('employee_login')
      .select('*')
      .eq('email', email)
      .is('logout_time', null)
      .order('login_time', { ascending: false })
      .limit(1)
      .single();
    if (fetchError || !latest) return { data: null, error: fetchError || { message: 'No active login found' } };
    const logout_time = this.getISTISOString();
    const { data, error } = await supabase
      .from('employee_login')
      .update({ logout_time })
      .eq('id', latest.id)
      .select();
    return { data, error };
  },
} 