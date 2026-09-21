<template>
    <div>
      <h1>Add New Book</h1>
      <form @submit.prevent="addBook">
        <div>
          <label for="name">Book Name:</label>
          <input type="text" v-model="name" required />
        </div>
        <div>
          <label for="authors">Authors:</label>
          <input type="text" v-model="authors" required />
        </div>
        <div>
          <label for="section">Section:</label>
          <select v-model="selectedSectionId" required>
            <option value="" disabled>Select a section</option>
            <option v-for="section in sections" :key="section.id" :value="section.id">
              {{ section.name }}
            </option>
          </select>
        </div>
        <div>
          <label for="pdf_file">PDF File:</label>
          <input type="file" @change="handleFileUpload" />
        </div>
        <button type="submit">Add Book</button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        name: '',
        authors: '',
        selectedSectionId: null,
        pdfFile: null,
        sections: [] // List of sections
      };
    },
    methods: {
      handleFileUpload(event) {
        this.pdfFile = event.target.files[0];
      },
      async addBook() {
        const formData = new FormData();
        formData.append('name', this.name);
        formData.append('authors', this.authors);
        formData.append('section', this.selectedSectionId);
        if (this.pdfFile) {
          formData.append('pdf_file', this.pdfFile);
        }
  
        try {
          const response = await axios.post('http://localhost:5000/librarian/add_book', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          alert(response.data.msg);
          this.$router.push('/librarian-dashboard');
        } catch (error) {
          console.error('Error adding book:', error.response ? error.response.data : error.message);
          alert('Failed to add book.');
        }
      },
      async fetchSections() {
        try {
          const response = await axios.get('http://localhost:5000/librarian/sections', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          this.sections = response.data.sections;
        } catch (error) {
          console.error('Failed to fetch sections:', error.response ? error.response.data : error.message);
        }
      }
    },
    created() {
      this.fetchSections();
    }
  };
  </script>
  