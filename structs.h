#ifndef STRUCTS_H_
#define STRUCTS_H_

struct User {
  unsigned int userid;        // must be greater than 0
  char username[50];          // can't contain characters like [,],\t,\n 
  char password[50];          // can't contain characters like [,],\t,\n 
  unsigned int friends[100];  // list of userids
  int socket;                 // socket descriptor of a particular user
  unsigned int is_active;     // boolean, 0 or 1
  pthread_mutex_t write_socket_lock;
} Users[100];

pthread_mutex_t users_lock;

#endif
