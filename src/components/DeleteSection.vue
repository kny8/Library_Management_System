<template>
    <div>
      <h1>Manage Sections</h1>
      <h2>Sections</h2>
      <ul>
        <li v-for="section in sections" :key="section.id">
          {{ section.name }}
          <button @click="deleteSection(section.id)">Delete</button>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        sections: []
      };
    },
    created() {
      this.fetchSections();
    },
    methods: {
      async fetchSections() {
        try {
          const response = await axios.get('http://localhost:5000/librarian/dashboard', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          this.sections = response.data.sections;
        } catch (error) {
          console.error('Error fetching sections:', error.response ? error.response.data : error.message);
        }
      },
      async deleteSection(sectionId) {
        try {
          const response = await axios.post(`http://localhost:5000/librarian/delete_section/${sectionId}`, null, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          alert(response.data.msg);
          this.fetchSections(); // Refresh the list
        } catch (error) {
          console.error('Error deleting section:', error.response ? error.response.data : error.message);
          alert('Failed to delete section.');
        }
      }
    }
  };
  </script>
  