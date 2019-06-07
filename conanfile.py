from conans import ConanFile, CMake, tools
import os


class SimpleAmqpClientConan(ConanFile):
    name = "simpleamqpclient"
    version = "2.5.0-pre3"
    license = "Apache License, Version 2.0"
    url = "https://github.com/alanxz/SimpleAmqpClient"
    settings = "os", "compiler", "build_type", "arch"
    #options = {"shared": [True, False]}
    #default_options = "shared=False"
    generators = "cmake"
    requires = (
                ("rabbitmq-c/[>=0.5.1]@external/release")
               ,("boost/[>=1.47.0]@external/release")
               )

    def source(self):
        self.run("git clone https://github.com/Rajas014/simpleamqpclient.git")
        self.run("cd simpleamqpclient)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file("simpleamqpclient/CMakeLists.txt", 'PROJECT(SimpleAmqpClient)', '''PROJECT(SimpleAmqpClient)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
if(MSVC)
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /MP /Z7")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /MP /Z7 /EHsc")
endif()
''')

        tools.replace_in_file("simpleamqpclient/Modules/FindRabbitmqc.cmake", 'NAMES rabbitmq', 'NAMES rabbitmq librabbitmq.4')
        #tools.replace_in_file("simpleamqpclient/CMakeLists.txt", 'TARGET_LINK_LIBRARIES(SimpleAmqpClient', 'TARGET_LINK_LIBRARIES(SimpleAmqpClient ${CONAN_LIBS}')
        tools.replace_in_file("simpleamqpclient/CMakeLists.txt", 'FATAL_ERROR', 'STATUS')
        tools.replace_in_file("simpleamqpclient/src/SimpleAmqpClient/Util.h", '#ifdef WIN32', '#ifdef WIN32___disable')

    def build(self):
        cmake = CMake(self)

        cmake.definitions["ENABLE_SSL_SUPPORT"] = "ON"
        cmake.definitions["Boost_USE_STATIC_LIBS"] = "ON"
        cmake.definitions["BUILD_SHARED_LIBS"] = "OFF"
        cmake.definitions["BUILD_STATIC_LIBS"] = "ON"

        cmake.configure(source_dir='simpleamqpclient', build_dir="./")
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include/SimpleAmqpClient", src="simpleamqpclient/src/SimpleAmqpClient")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []
        if self.settings.os == "Windows":
            self.cpp_info.libs.append('SimpleAmqpClient.2')
        else:
            self.cpp_info.libs.append('SimpleAmqpClient')
