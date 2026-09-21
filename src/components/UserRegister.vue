<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div>
        <label for="username">Username:</label>
        <input type="text" v-model="username" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" required />
      </div>
      <div>
        <label for="role">Role:</label>
        <select v-model="role" required>
          <option value="librarian">Librarian</option>
          <option value="user">User</option>
        </select>
      </div>
      <button type="submit">Register</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      role: 'user' // Default selection
    };
  },
  methods: {
    async register() {
      try {
        const response = await axios.post('http://localhost:5000/register', {
          username: this.username,
          password: this.password,
          role: this.role
        });
        alert(response.data.msg);
      } catch (error) {
        console.error('Registration error:', error.response ? error.response.data : error.message);
        alert('Failed to register user.');
      }
    }
  }
};
</script>
