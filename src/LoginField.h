#ifndef __LOGIN_FIELD_H
#define __LOGIN_FIELD_H

#include <iostream>
#include <string>
#include <termios.h>
#include <unistd.h>

//#define WIN32
#ifdef WIN32
#include <windows.h>
#endif

class LoginField
{
 public:
  LoginField() {}
  ~LoginField() {}

  void readPass(std::string);
  void readUser(std::string);

  std::string pass() {return password;}
  std::string user() {return username;}

 private:
  std::string username;
  std::string password;

  void SetStdinEcho(bool);
};

#endif //__LOGIN_FIELD_H
