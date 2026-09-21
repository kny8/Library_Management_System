<template>
    <div>
      <h2>Add Section</h2>
      <form @submit.prevent="addSection">
        <div>
          <label for="name">Section Name:</label>
          <input type="text" v-model="name" required />
        </div>
        <div>
          <label for="description">Description:</label>
          <textarea v-model="description" required></textarea>
        </div>
        <button type="submit">Add Section</button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        name: '',
        description: ''
      };
    },
    methods: {
      async addSection() {
        try {
          // Make a POST request to add the section
          await axios.post('http://localhost:5000/librarian/add_section', {
            name: this.name,
            description: this.description
          }, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}` // Add authorization header
            }
          });
  
          // Navigate to the librarian dashboard upon successful addition
          this.$router.push('/librarian-dashboard');  
        } catch (error) {
          // Handle any errors that occur during the request
          console.error('Failed to add section:', error.response ? error.response.data : error.message);
          alert('Failed to add section.');
        }
      }
    }
  };
  </script>
  