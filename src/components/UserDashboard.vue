<template>
  <div>
    <h1>Welcome, {{ username }}!</h1>

    <!-- Display Sections -->
    <h2>Sections</h2>
    <div v-if="Object.keys(sections).length > 0">
      <div v-for="(books, section) in sections" :key="section">
        <h3>{{ section }}</h3>
        <ul>
          <li v-for="book in books" :key="book.id">
            {{ book.name }} - {{ book.authors }}
            <button @click="requestBook(book.id)" v-if="book.requestStatus !== 'Read'">Request</button>
            <!-- Show Read Button if request status is 'Read' -->
            <button v-if="book.requestStatus === 'Read'" @click="readBook(book.pdf_file)">Read</button>
          </li>
        </ul>
      </div>
    </div>
    <div v-else>
      <p>No books available.</p>
    </div>

    <!-- Link to Accepted Books -->
    <div>
      <router-link to="/accepted_books">View Accepted Books</router-link>
    </div>

    <!-- Logout button -->
    <button @click="logout">Logout</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      sections: {}
    };
  },
  methods: {
    async fetchDashboardData() {
      try {
        const response = await axios.get('http://localhost:5000/user/dashboard', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.username = response.data.username;
        this.sections = response.data.sections;
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      }
    },
    async requestBook(bookId) {
      try {
        await axios.post(`http://localhost:5000/user/request_book/${bookId}`, null, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        alert('Book requested successfully!');
      } catch (error) {
        console.error('Failed to request book:', error);
      }
    },
    readBook(pdfFile) {
      // Redirect to PDF view page
      window.open(`http://localhost:5000/uploads/${pdfFile}.pdf`, '_blank');
    },
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  },
  created() {
    this.fetchDashboardData();
  }
};
</script>
