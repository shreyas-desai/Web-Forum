# Web-Forum

Shreyas Desai
sdesai33@stevens.edu

Chaitanya Ratnaparkhi
cratnapa@stevens.edu

Prasanna Limaye
plimaye@stevens.edu

Github URL: https://github.com/shreyas-desai/Web-Forum

Each of us spent around 5-6 hours to implement this project

## Code Overview:

The codebase is structured as a Flask application and utilizes SQLite as the database. The application includes features such as user creation, posting messages, threaded replies, and date-based queries.

## Testing Methodology:

We conducted thorough testing to ensure the reliability and functionality of our code. Our testing approach included unit testing with postman API, we tested all the endpoints with edge cases to ensure effective working of the code. </br>
We have used forum_sample_tests.postman_collection.json to test in postman.
</br> The usage of the endpoints is described in the postman collection

## Bugs and Issues:

No

## Difficult Issue Resolution Example:

### Issue:

One challenging bug involved user-based range queries not producing accurate results. Users were not able to retrieve the desired information based on specified ranges.

### Resolution:

To tackle this issue, we revisited our database queries and found an oversight in our filtering logic. We adjusted the query parameters and implemented additional checks to ensure accurate range-based results.

## Current Extensions:

1. **User and User Keys:**

   - Implemented a user authentication system for secure access to the forum.

2. **User Profiles:**

   - Users can create and customize their profiles with personal information.

3. **Threaded Replies:**

   - Enabled threaded discussions for more organized and engaging conversations.

4. **User-Based Range Queries:**

   - Implemented the ability for users to query and filter content based on specified ranges.

5. **Date and Time-Based Queries:**
   - Users can perform queries based on specific dates and times, enhancing content search capabilities.

## Usage Instructions:

#   Endpoint
    /post
This endpoint is used to create a post with `"msg"` key which has the content of the message to be posted.
Request:
```json
{
    "msg": "hello"
}
```
Response:
```json
{
    "id": 1,
    "key": "RhBqxFHT-ioQWHo-DaWDGmnpw_OuYxi5s_ya1dgzhgE",
    "msg": "hello",
    "timestamp": "2023-12-18T03:35:03.271453+00:00"
}
```
#   Endpoint
    /post/{{id}}

#   Endpoint
    /post/{{id}}/delete/{{key}}

#   Endpoint
    /post/{{childid}}

#   Endpoint
    /user


#   Endpoint
    /post/{{userid}}

#   Endpoint
    /post/{{id}}/delete/{{userkey}}

    
#   Endpoint
    /user/{{uname}}

#   Endpoint
    /postsByDate?startDate={{startdate}}

#   Endpoint
    /postsByDate?endDate={{enddate}}

1. **Post Creation:**

   - To create a post, send a POST request to the `/post` endpoint with a JSON payload containing the "msg" field.

2. **User Creation:**

   - To create a user, send a POST request to the `/user` endpoint with a JSON payload containing "uname," "fname," and "lname" fields.

3. **Post Retrieval:**

   - Retrieve posts by sending a GET request to the `/post` endpoint. You can filter by user using the `user` query parameter.

4. **Date-Based Queries:**

   - Utilize the `/postsByDate` endpoint with `startDate` and/or `endDate` query parameters to retrieve posts within a specified date range.

5. **Post Deletion:**
   - Delete a post by sending a DELETE request to the `/post/<post_id>/delete/<key>` endpoint, providing the post ID and the associated key.
