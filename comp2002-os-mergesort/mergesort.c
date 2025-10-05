/**
 * This file implements parallel mergesort.
 */

#include "mergesort.h"
#include <stdio.h>
#include <stdlib.h> /* for malloc */
#include <string.h> /* for memcpy */

/* global vars
int *A = input array
int *B = Extra storage for merge sort
int cutoff = number of levels of division
struct argument {
    int left;
    int right;
    int level;
};
*/

void print_array_(int left, int right, int *array) {
    while (left <= right) {
        printf("%d, ", array[left]);
        left++;
    }
    printf("\n");
}

// using coarse lock for now, can be optimized to use a different lock for each thread
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

/* this function will be called by mergesort() and also by parallel_mergesort().
the bounds are inclusive
*/
void merge(int leftstart, int leftend, int rightstart, int rightend) {
    // printf("before merge:\n");
    // print_array_(leftstart, rightend, A);

    // using a naive approach
    // place into B in sorted order
    // then copy back into A
    int left_index = leftstart;
    int right_index = rightstart;
    int target_index = leftstart;
    while (left_index <= leftend && right_index <= rightend) {
        if (A[left_index] <= A[right_index]) {
            B[target_index] = A[left_index];
            left_index++;
        } else {
            B[target_index] = A[right_index];
            right_index++;
        }
        target_index++;
    }
    // print_array_(leftstart, rightend, B);
    // printf("left_index; %d, right_index %d\n", left_index, right_index);

    while (left_index <= leftend) {
        // printf("adding from left\n");
        B[target_index] = A[left_index];
        left_index++;
        target_index++;
    }

    while (right_index <= rightend) {
        // printf("adding from right\n");
        B[target_index] = A[right_index];
        right_index++;
        target_index++;
    }

    // print_array_(leftstart, rightend, B);
    int i = leftstart;
    while (i <= rightend) {
        A[i] = B[i];
        i++;
    }

    // printf("after merge:\n");
    // print_array_(leftstart, rightend, A);
}

/* this function will be called by parallel_mergesort() as its base case. */
void my_mergesort(int left, int right) {
    // base case with 1 element array
    // can be updated to 16-32 for better performance
    if (left >= right) {
        return;
    }

    int middle = (left + right) / 2;
    my_mergesort(left, middle);
    my_mergesort(middle + 1, right);

    merge(left, middle, middle + 1, right);
}

/* this function will be called by the testing program. */
void *parallel_mergesort(void *arg) {
    struct argument *args = (struct argument *)arg;
    // printf("left: %d, right: %d, levels: %d\n", args->left, args->right, args->level);
    // print_array_(args->left, args->right, A);

    if (args->level == cutoff) {
        my_mergesort(args->left, args->right);
        return NULL;
    }
    int middle = (args->left + args->right) / 2;
    struct argument *left_args = buildArgs(args->left, middle, args->level + 1);
    struct argument *right_args = buildArgs(middle + 1, args->right, args->level + 1);

    pthread_t left_thread;
    pthread_t right_thread;
    pthread_create(&left_thread, NULL, parallel_mergesort, left_args);
    pthread_create(&right_thread, NULL, parallel_mergesort, right_args);
    pthread_join(left_thread, NULL);
    pthread_join(right_thread, NULL);

    merge(args->left, middle, middle + 1, args->right);

    // print_array_(args->left, args->right, A);
    return NULL;
}

/* we build the argument for the parallel_mergesort function. */
struct argument *buildArgs(int left, int right, int level) {
    struct argument *args = malloc(sizeof(struct argument));
    if (args == NULL) {
        perror("malloc failed");
        exit(1);
    }
    args->left = left;
    args->right = right;
    args->level = level;
    return args;
}
