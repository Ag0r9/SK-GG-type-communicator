#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <pthread.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include "structs.h"

#define MAX_MESSAGE_LENGTH 8192

int NO_HEADER_NO_MESSAGE = 1;
int HEADER = 2;
int MESSAGE = 3;
int NB_CLIENTS = 0;

void send_message(char* header, char* content, int fd) {
  char response[strlen(header)+strlen(content)+3];
  bzero(response, strlen(header)+strlen(content)+3);

  //char* response = "\t";

  strcat(response, "\t");
  strcat(response, header);
  strcat(response, "\t");
  strcat(response, content);
  strcat(response, "\t");
  printf("Response: %s\n", response);

  int res = send(fd, response, strlen(response), 0);

  if (res<1) {
    perror("Error with send(): ");

  }
}

void reverse(char s[]) {
     int i, j;
     char c;

     for (i = 0, j = strlen(s)-1; i<j; i++, j--) {
         c = s[i];
         s[i] = s[j];
         s[j] = c;
     }
}

void itoa(int n, char s[]) {
     int i;
     i = 0;
     do {
         s[i++] = (n%10)+'0';
     } while ((n /= 10) > 0);
     s[i] = '\0';
     reverse(s);
}

int find_id(int response_socket) {
  unsigned int id;
  for (int i=0; i<NB_CLIENTS; ++i) {
    if (Users[i].socket == response_socket) {
      id = Users[i].userid;
      return id;
    }
  }
  return -1;
}

/*
 * char* operation      string which contains the operation (undetermined length, max 1024)
 * char* message        string with a received message (undetermined length, max 1024)
 * int response_socket  socket to send response to
 */

void take_action(char* operation, char* message, int response_socket) {

// SIGNUP:
// operation: "SIGNUP"
// message:   "username password"
// response:
//    operation:  "SIGNUP_RESP SUCCESS" or "SIGNUP_RESP FAILED"
//    message:    if failed: "USERNAME_TAKEN" or "LIST_IS_FULL"

if (!strcmp(operation, "SIGNUP")) {
  printf("REJESTROWANKO\n");
  pthread_mutex_lock(&users_lock);
  if (NB_CLIENTS >= 100) {
    int id = find_id(response_socket);
    pthread_mutex_lock(&Users[id].write_socket_lock);
    send_message("SIGNUP_R FAILED", "LIST_IS_FULL", response_socket);
    pthread_mutex_unlock(&Users[id].write_socket_lock);
    return;
  } else {
    char username[50];
    bzero(username, 50);
    char password[50];
    bzero(password, 50);
    for (int i=0; i<strlen(message); ++i) {
      if (message[i]==32) {
        strncpy(username, message, i);
        strcpy(password, message + i);
        break;
      }
    }
    for (int i=0; i<NB_CLIENTS; ++i) {
      if (!strcmp(Users[i].username, username)) {
        pthread_mutex_lock(&Users[i].write_socket_lock);
        send_message("SIGNUP_R FAILED", "USERNAME_TAKEN", response_socket);
        pthread_mutex_unlock(&Users[i].write_socket_lock);
        pthread_mutex_unlock(&users_lock);
        return;
      }
    }
    Users[NB_CLIENTS].userid = NB_CLIENTS;
    strcpy(Users[NB_CLIENTS].username, username);
    strcpy(Users[NB_CLIENTS].password, password);
    Users[NB_CLIENTS].friends[NB_CLIENTS] = 1;
    pthread_mutex_lock(&Users[NB_CLIENTS].write_socket_lock);
printf("%d %s %s\n", Users[NB_CLIENTS].userid, Users[NB_CLIENTS].username, Users[NB_CLIENTS].password);
    send_message("SIGNUP_R SUCCESS", "SUCCESS", response_socket);
    pthread_mutex_unlock(&Users[NB_CLIENTS].write_socket_lock);
    pthread_mutex_unlock(&users_lock);
    NB_CLIENTS++;
  }
}

// LOGIN:
// operation: "LOGIN"
// message:   "username password"
// response:
//    operation:  "LOGIN_RESP SUCCESS" or "LOGIN_RESP FAILED"
//    message:    if failed: "NO_SUCH_USER" or "WRONG_USERNAME_OR_PASSWORD" or "ALREADY_LOGGED"

if (!strcmp(operation, "LOGIN")) {
    printf("LOGOWANKO\n");
    char username[50];
    bzero(username, 50);
    char password[50];
    bzero(username, 50);
    for (int i=0; i<strlen(message); ++i) {
      if (message[i]==32) {
        strncpy(username, message, i);
        strcpy(password, message + i);
        break;
      }
    }
    pthread_mutex_lock(&users_lock);
    printf("%d\n", NB_CLIENTS);
    for(int i=0; i<NB_CLIENTS; ++i) {
	    printf("%s %s\n", Users[i].username, username);
      if (!strcmp(Users[i].username, username)) {
        if (Users[i].is_active == 1) {
          pthread_mutex_lock(&Users[i].write_socket_lock);
          send_message("LOGIN_R FAILED", "ALREADY_LOGGED", response_socket);
          pthread_mutex_unlock(&Users[i].write_socket_lock);
          pthread_mutex_unlock(&users_lock);
          return;
        }

        if (!strcmp(Users[i].password, password)) {
          Users[i].socket = response_socket;
          Users[i].is_active = 1;
          pthread_mutex_lock(&Users[i].write_socket_lock);
printf("%s a %s d %s\n", Users[i].password, password, Users[i].username);
          send_message("LOGIN_R SUCCESS", "SUCCESS", response_socket);
          pthread_mutex_unlock(&Users[i].write_socket_lock);
          pthread_mutex_unlock(&users_lock);
          return;
        }
        else {
          pthread_mutex_lock(&Users[i].write_socket_lock);
          send_message("LOGIN_R FAILED", "WRONG_USER_OR_PASSWORD", response_socket);
          pthread_mutex_unlock(&Users[i].write_socket_lock);
          pthread_mutex_unlock(&users_lock);
          return;
        }
      }
    }
    int id = find_id(response_socket);
    printf("%d\n", id);
    pthread_mutex_lock(&Users[id].write_socket_lock);
printf("%s a %s d %s\n", Users[id].password, password, Users[id].username);
    send_message("LOGIN_R FAILED", "NO_SUCH_USER", response_socket);
    pthread_mutex_unlock(&Users[id].write_socket_lock);
    pthread_mutex_unlock(&users_lock);
    return;
}

// ADD FRIEND:
// operation: "ADD_FRIEND"
// message:   "username"
// response:
//    operation: "ADD_FRIEND_RESP SUCCESS" or "ADD_FRIEND_RESP FAILED" 
//    message:   if failed: "NO_SUCH_USER" or "ALREADY_FRIENDS"

if (!strcmp(operation, "ADD_FRIEND")) {
  printf("DODAWANKO");
  int friend_id = -1;
  int client_id = -1;
  pthread_mutex_lock(&users_lock);
  for (int i=0; i<NB_CLIENTS; ++i) {
    if (!strcmp(message, Users[i].username)) {
      friend_id = Users[i].userid;
      break;
    }
  }
  client_id = find_id(response_socket);
  if (friend_id == -1) {
    pthread_mutex_lock(&Users[client_id].write_socket_lock);
    send_message("ADD_FRIEND_R FAILED", "NO_SUCH_USER", response_socket);
    pthread_mutex_unlock(&Users[client_id].write_socket_lock);
    pthread_mutex_unlock(&users_lock);
    return;
  }
  
  if (Users[client_id].friends[friend_id] == 1) {
    pthread_mutex_lock(&Users[client_id].write_socket_lock);
    send_message("ADD_FRIEND_R FAILED", "ALREADY_FRIENDS", response_socket);
    pthread_mutex_unlock(&Users[client_id].write_socket_lock);
    pthread_mutex_unlock(&users_lock);
    return;
  } else {
    Users[client_id].friends[friend_id] = 1;
    pthread_mutex_lock(&Users[client_id].write_socket_lock);
    send_message("ADD_FRIEND_R SUCCESS", "SUCCESS", response_socket);
    pthread_mutex_unlock(&Users[client_id].write_socket_lock);
    pthread_mutex_unlock(&users_lock);
    return;
  }
}

// REMOVE FRIEND:
// operation: "REMOVE_FRIEND"
// message:   "userid"
// response:
//    operation: "REMOVE_FRIEND_RESP SUCCESS" or "REMOVE_FRIEND_RESP FAILED" 
//    message:   if failed: "NOT_FRIENDS"

if (!strcmp(operation, "REMOVE_FRIEND")) {
  printf("USUWANKO");
  int friend_id = -1;
  int client_id = -1;
  pthread_mutex_lock(&users_lock);
  for (int i=0; i<NB_CLIENTS; ++i) {
    if (!strcmp(message, Users[i].username)) {
      friend_id = Users[i].userid;
      break;
    }
  }
  client_id = find_id(response_socket);
  if (Users[client_id].friends[friend_id] == 0) {
    pthread_mutex_lock(&Users[client_id].write_socket_lock);
    send_message("REMOVE_FRIEND_R FAILED", "NOT_FRIENDS", response_socket);
    pthread_mutex_unlock(&Users[client_id].write_socket_lock);
    pthread_mutex_unlock(&users_lock);
    return;
  } else {
    Users[client_id].friends[friend_id] = 0;
    pthread_mutex_lock(&Users[client_id].write_socket_lock);
    send_message("REMOVE_FRIEND_R SUCCESS", "SUCCESS", response_socket);
    pthread_mutex_unlock(&Users[client_id].write_socket_lock);
    pthread_mutex_unlock(&users_lock);
    return;
  }
}
 
// FRIENDS LIST:
// operation: "FRIENDS_LIST"
// message:   ""
// response: 
//    operation: "FRIENDS_LIST_RESP"
//    message:   "[userid isactive username] [userid isactive username] [userid isactive username]"

if (!strcmp(operation, "FRIENDS_LIST")) {
  printf("LISTOWANKO");
  int client_id;
  pthread_mutex_lock(&users_lock);
  client_id = find_id(response_socket);

char list[8192];
strcpy(list, "");
 char s[10];
  for(int i=0; i<NB_CLIENTS; ++i) {
    if ((Users[client_id].friends[i] == 1) && (client_id != i)) {
      strcat(list, "[");
      strcpy(s, "");
      itoa(Users[i].userid, s);
      strcat(list,  s);
      strcpy(s, "");
      itoa(Users[i].is_active, s);
      strcat(list, " ");
      strcat(list, s);
      strcat(list, " ");
      strcat(list, Users[i].username);
      strcat(list, "] ");
    }
  }
  printf("%s", list);
  pthread_mutex_lock(&Users[client_id].write_socket_lock);
  send_message("FRIENDS_LIST_R SUCCESS", list, response_socket); //blad??
  pthread_mutex_unlock(&Users[client_id].write_socket_lock);
  pthread_mutex_unlock(&users_lock);
  return;
}

// SEND MESSAGE:
// operation: "SEND_MESSAGE"
// message:   "user_id content of the message goes here"

if (!strcmp(operation, "SEND_MESSAGE")) {
  printf("WYSYLANKO");
  int client_id = -1;
  char id_text[3];
  char text[1020];
  pthread_mutex_lock(&users_lock);
  client_id = find_id(response_socket);
  for (int i=0; i<strlen(message); ++i) {
      if (message[i]==32) {
        strncpy(id_text, message, i);
        client_id = atoi(id_text);
        strcpy(text, message + i);
        break;
      }
  }
  pthread_mutex_lock(&Users[client_id].write_socket_lock);
  send_message("SEND_MESSAGE_R SUCCESS", "SUCCESS", response_socket);
  pthread_mutex_unlock(&Users[client_id].write_socket_lock);
  pthread_mutex_lock(&Users[Users[client_id].socket].write_socket_lock);
  send_message("GET_MESSAGE_R SUCCESS", text, Users[client_id].socket);
  pthread_mutex_unlock(&Users[Users[client_id].socket].write_socket_lock);
  pthread_mutex_unlock(&users_lock);
  return;
}

//LOGOUT
// operation: "LOGOUT"
// message:   ""
// response: 
//    operation: "LOGOUT_RESP"

  if (!strcmp(operation, "LOGOUT")) {
    printf("WYLOGOWANKO");
    pthread_mutex_lock(&users_lock);
    for (int i=0; i<NB_CLIENTS; ++i) {
      if (Users[i].socket == response_socket) {
        Users[i].is_active = 0;
        pthread_mutex_lock(&Users[i].write_socket_lock);
        send_message("LOGOUT_R SUCCESS", "SUCCESS", response_socket);
        pthread_mutex_unlock(&Users[i].write_socket_lock);
        pthread_mutex_unlock(&users_lock);
        break;
      }
    }
    return;
  }
}

void* handle_connection(void *arg) {
  
  int passed_desc = *(int*)arg; // deskryptor klienta

  printf("New thread has started. It serves a connection #%d\n", passed_desc);

  char operation[MAX_MESSAGE_LENGTH];
  char content[MAX_MESSAGE_LENGTH];

  bzero(operation, MAX_MESSAGE_LENGTH);
  bzero(content, MAX_MESSAGE_LENGTH);

  char buffer[1];
  bzero(buffer, 1);
  int state = NO_HEADER_NO_MESSAGE;
  int count = 0;

  while((count = recv(passed_desc, buffer, 1, 0)) > 0) {

    if (state==NO_HEADER_NO_MESSAGE) {
      if (buffer[0] == '\t') {
        state = HEADER;  
      }

    } else if (state==HEADER) {

      if (buffer[0] == '\t') {
        state = MESSAGE;
      } else {
        strncat(operation, buffer, 1);
      }
      
    } else if (state==MESSAGE) {
      if (buffer[0] == '\t') {
        printf("Operacyjka: %s Wiadomosc: %s\n", operation, content);
        take_action(operation, content, passed_desc);
	bzero(operation, MAX_MESSAGE_LENGTH);
	bzero(content, MAX_MESSAGE_LENGTH);
	state = NO_HEADER_NO_MESSAGE;
      } else {strncat(content, buffer, 1);
      }
    }

  }

  if (count == -1) {
    printf("Error when receiving, client descriptor %d\n", passed_desc);
  } else if (count == 0) {
    printf("Connection ended with client #%d\n", passed_desc);
  }

  printf("Terminating thread of connection #%d\n", passed_desc);

  return 0;

}

int main() {

  int fd = socket(AF_INET, SOCK_STREAM, 0); // Main file descriptor of the socket

  if (fd < 0) {
    perror("Error while creating the socket: ");
    exit(-1);
  }

  if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) < 0) {
    perror("setsockopt(SO_REUSEADDR) failed");
  }

  struct sockaddr_in server_addr;
  memset(&server_addr, 0, sizeof(server_addr));

  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(8021); // PORT on which server is running
  server_addr.sin_addr.s_addr = INADDR_ANY;
  
  if (bind(fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
    perror("Error when binding: ");
    return -1;
  }

  if (listen(fd, 128) < 0) {
    perror("Error when starting to listen: ");
    return -1;
  }

  struct sockaddr_in client_address;
  socklen_t client_address_size = sizeof(client_address);


  while(1) {
  
    int client_fd = accept(fd, (struct sockaddr *)&client_address, &client_address_size);

    pthread_t new_thread;
    
    int thread_result = pthread_create(&new_thread, NULL, handle_connection, &(int){client_fd});

    if (thread_result < 0) {
      printf("There was an error with creating a new thread.\n");
      exit(-1);
    }

    pthread_detach(new_thread);
  }


  return 0;
}
