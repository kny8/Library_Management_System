<template>
  <div>
    <h1>Welcome, {{ username }}!</h1>
    
    <!-- Search form -->
    <form @submit.prevent="searchBooks">
      <label for="search">Search Books:</label>
      <input type="text" id="search" v-model="searchQuery" placeholder="Enter book name or author" />
      <button type="submit">Search</button>
    </form>
    
    <!-- Display search results -->
    <h2>Search Results</h2>
    <ul>
      <li v-for="book in searchResults" :key="book.id">
        {{ book.name }} - {{ book.authors }}
        <ul>
          <li><router-link :to="{ name: 'editBook', params: { bookId: book.id } }">Edit</router-link></li>
          <li><button @click="deleteBook(book.id)">Delete</button></li>
        </ul>
      </li>
    </ul>
    
    <!-- Display Sections -->
    <h2>Sections</h2>
    <ul>
      <li v-for="section in sections" :key="section.id">
        {{ section.name }}
        <ul>
          <li><router-link :to="{ name: 'editSection', params: { sectionId: section.id } }">Edit</router-link></li>
          <li><button @click="deleteSection(section.id)">Delete</button></li>
        </ul>
      </li>
    </ul>
    
    <!-- Display Books -->
    <h2>Books</h2>
    <ul>
      <li v-for="book in books" :key="book.id">
        {{ book.name }} - {{ book.authors }}
        <ul>
          <li><router-link :to="{ name: 'editBook', params: { bookId: book.id } }">Edit</router-link></li>
          <li><button @click="deleteBook(book.id)">Delete</button></li>
        </ul>
      </li>
    </ul>

    <!-- Links to add new section and book -->
    <p><router-link to="/add-section">Add Section</router-link></p>
    <p><router-link to="/add-book">Add Book</router-link></p>
    
    <!-- Link to book requests -->
    <p><router-link to="/book-requests">Book Requests</router-link></p>
    
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
      searchQuery: '',
      searchResults: [],
      sections: [],
      books: []
    };
  },
  methods: {
    async fetchDashboardData() {
      try {
        const response = await axios.get('http://localhost:5000/librarian/dashboard', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.username = response.data.username;
        this.sections = response.data.sections;
        this.books = response.data.books;
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      }
    },
    async searchBooks() {
      try {
        const response = await axios.get('http://localhost:5000/search_books', {
          params: { query: this.searchQuery },
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.searchResults = response.data.books;
      } catch (error) {
        console.error('Failed to search books:', error);
      }
    },
    async deleteBook(bookId) {
      try {
        await axios.post(`http://localhost:5000/librarian/delete_book/${bookId}`, null, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.fetchDashboardData(); // Refresh data after deletion
      } catch (error) {
        console.error('Failed to delete book:', error);
      }
    },
    async deleteSection(sectionId) {
      try {
        await axios.post(`http://localhost:5000/librarian/delete_section/${sectionId}`, null, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.fetchDashboardData(); // Refresh data after deletion
      } catch (error) {
        console.error('Failed to delete section:', error);
      }
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
