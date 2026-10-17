cmake_minimum_required(VERSION 3.22.1)

project("litert_indic" LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags for ARM Cortex-A53 (Lenovo Tab K10)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -fvisibility=hidden -fexceptions -frtti")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -fvisibility=hidden")

add_library(litert_indic SHARED
    jni_bridge.cpp
    litert_indic_engine.cpp
    euler_sampler.cpp
    audio_processor.cpp
    indic_tokenizer.cpp
    tflite_loader.cpp
    kissfft/kiss_fft.c
    kissfft/kiss_fftr.c
)

target_include_directories(litert_indic PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/kissfft
)

target_link_libraries(litert_indic PRIVATE
    log
    android
    m
    dl
)
