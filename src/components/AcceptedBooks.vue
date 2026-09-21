<template>
    <div>
      <h1>Accepted Books</h1>
      <div v-if="books.length > 0">
        <ul>
          <li v-for="book in books" :key="book.id">
            {{ book.name }} - {{ book.authors }}
            <button @click="readBook(book.id)">Read</button>
          </li>
        </ul>
      </div>
      <div v-else>
        <p>No accepted books available.</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        books: []
      };
    },
    methods: {
      async fetchAcceptedBooks() {
        try {
          const response = await axios.get('http://localhost:5000/user/accepted_books', {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          console.log('Fetched books:', response.data.books); // Debugging line
          this.books = response.data.books;
        } catch (error) {
          console.error('Failed to fetch accepted books:', error);
        }
      },
      async readBook(bookId) {
        try {
          const response = await axios.get(`http://localhost:5000/user/read_book/${bookId}`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            },
            responseType: 'blob'
          });
          const url = URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.download = 'book.pdf'; // Set filename as needed
          link.click();
          URL.revokeObjectURL(url);
        } catch (error) {
          console.error('Failed to read book:', error);
        }
      }
    },
    created() {
      this.fetchAcceptedBooks(); // Fetch accepted books when component is created
    }
  };
  </script>
  
  <style>
  /* Add styles as needed */
  </style>
  