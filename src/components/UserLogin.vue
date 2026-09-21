<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div>
        <label for="username">Username:</label>
        <input type="text" v-model="username" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:5000/login', {
          username: this.username,
          password: this.password
        });
        const token = response.data.access_token;
        const role = response.data.role; // Get role from the response
        localStorage.setItem('token', token);
        
        // Redirect based on role
        if (role === 'librarian') {
          this.$router.push('/librarian-dashboard');
        } else if (role === 'user') {
          this.$router.push('/user-dashboard');
        }
      } catch (error) {
        console.error('Login error:', error.response ? error.response.data : error.message);
        alert('Failed to login.');
      }
    }
  }
};
</script>
