<template>
  <div>
    <h2>Edit Section</h2>
    <form @submit.prevent="updateSection">
      <div>
        <label for="name">Section Name:</label>
        <input type="text" v-model="name" required />
      </div>
      <div>
        <label for="description">Description:</label>
        <textarea v-model="description" required></textarea>
      </div>
      <button type="submit">Update Section</button>
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
  async created() {
    try {
      const sectionId = this.$route.params.sectionId;
      const response = await axios.get(`http://localhost:5000/librarian/section/${sectionId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      const { name, description } = response.data;
      this.name = name;
      this.description = description;
    } catch (error) {
      console.error('Failed to fetch section data:', error.response ? error.response.data : error.message);
    }
  },
  methods: {
    async updateSection() {
      try {
        const sectionId = this.$route.params.sectionId;
        await axios.put(`http://localhost:5000/librarian/update_section/${sectionId}`, {
          name: this.name,
          description: this.description
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.$router.push('/librarian-dashboard');
      } catch (error) {
        console.error('Failed to update section:', error.response ? error.response.data : error.message);
        alert('Failed to update section.');
      }
    }
  }
};
</script>
