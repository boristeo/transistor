cmake_minimum_required(VERSION 3.12)

project(transistor VERSION 0.1)

# Dependencies for all subprojects
find_package(GTest REQUIRED)
find_package(Threads REQUIRED)
find_package(verilator REQUIRED)

macro(add_gtest TESTNAME)
  add_executable(${TESTNAME} ${ARGN})
  target_link_libraries(${TESTNAME} PUBLIC gtest gtest_main Threads::Threads)
  gtest_discover_tests(${TESTNAME}
      WORKING_DIRECTORY ${PROJECT_DIR}
  )
  set_target_properties(${TESTNAME} PROPERTIES FOLDER tests)
endmacro()


# Subprojects
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/src/uart)
