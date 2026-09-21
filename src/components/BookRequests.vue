<template>
  <div>
    <h1>Book Requests</h1>
    <table border="1">
      <thead>
        <tr>
          <th>Request ID</th>
          <th>User ID</th>
         
          <th>Book ID</th>
          <th>Book</th>
          <th>Timestamp</th>
          <th>Status</th>
          
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="request in requests" :key="request.id">
          <td>{{ request.id }}</td>
          <td>{{ request.user_id }}</td>
          
          <td>{{ request.book_id }}</td>
          <td>{{ request.book_name }}</td>
          <td>{{ request.timestamp }}</td>
          <td>{{ request.status }}</td>
          
          <td>
            <button @click="acceptRequest(request.id)">Accept</button>
            <button @click="denyRequest(request.id)">Deny</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const requests = ref([]);

    const fetchRequests = async () => {
      try {
        const response = await axios.get('http://localhost:5000/librarian/book_requests', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        requests.value = response.data.requests; // Extract 'requests' from response
      } catch (error) {
        console.error('Failed to fetch requests:', error);
        alert('Failed to load requests.');
      }
    };

    const acceptRequest = async (requestId) => {
      try {
        await axios.post(`http://localhost:5000/librarian/accept_request/${requestId}`, null, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        fetchRequests();
      } catch (error) {
        console.error('Failed to accept request:', error);
        alert('Failed to accept request.');
      }
    };

    const denyRequest = async (requestId) => {
      try {
        await axios.post(`http://localhost:5000/librarian/deny_request/${requestId}`, null, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        fetchRequests();
      } catch (error) {
        console.error('Failed to deny request:', error);
        alert('Failed to deny request.');
      }
    };

    onMounted(fetchRequests);

    return { requests, acceptRequest, denyRequest };
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>