/*
 * This file is part of sp-rich-core
 *
 * Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies). 
 *
 * Contact: Eero Tamminen <eero.tamminen@nokia.com>
 *
 * Copyright (C) 2013 Jolla Ltd.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License 
 * version 2 as published by the Free Software Foundation. 
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
 * 02110-1301 USA
 *
 */  

#define _GNU_SOURCE 1
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <errno.h>

const char RICHCORE_HEADER[] = "\n[---rich-core: ";
#define RICHCORE_HEADER_LEN sizeof (RICHCORE_HEADER) - 1

const char RICHCORE_HEADER_END[] = "---]\n";
#define RICHCORE_HEADER_END_LEN sizeof (RICHCORE_HEADER_END) - 1

const char *usage = "%s <input filename> [<output directory>]\n";

#define BUFFER_SIZE 4096 + 128
char buffer[BUFFER_SIZE];
size_t buffer_len = 0;
int at_input_beginning = 1;

static size_t find_substring(const char *mem, size_t mem_len,
                             const char *str, size_t str_len)
{
    if (str == NULL || str_len == 0 || mem == NULL || mem_len == 0) {
        return 0;
    }

    size_t i;
    int str_overhang = 0;
    for (i = 0; i < mem_len; ++i) {
        str_overhang = i + str_len - mem_len;
        if(str_overhang < 0) {
            str_overhang = 0;
        }

        if (strncmp(mem + i, str, str_len - str_overhang) == 0) {
            break;
        }
    }

    return i;
}

static size_t buffer_replenish(FILE *input_file)
{
    size_t bytes_read = fread(buffer + buffer_len, 1, BUFFER_SIZE - buffer_len,
                    input_file);
    buffer_len += bytes_read;

    return bytes_read;
}

static void buffer_flush(FILE *output_file, size_t byte_count)
{
    if (output_file != NULL) {
        fwrite(buffer, 1, byte_count, output_file);
    }
    memmove(buffer, buffer + byte_count, buffer_len -= byte_count);
}

static void write_data_until_header_beginning(FILE *input_file, FILE *output_file)
{
    buffer_replenish(input_file);

    while (1) {
        size_t header_begin;
        size_t header_len = RICHCORE_HEADER_LEN;

        if (at_input_beginning) {
            /* Special case - at the beginning of input file we allow to omit
             * initial '\n' of RICHCORE_HEADER. */
            at_input_beginning = 0;
            header_len -= 1;
            header_begin = find_substring(buffer, buffer_len,
                            RICHCORE_HEADER + 1, header_len);
            if (header_begin != 0) {
                continue;
            }
        } else {
            header_begin = find_substring(buffer, buffer_len,
                    RICHCORE_HEADER, header_len);
        }

        /* Write everything that precedes the header into previous file and
         * align the data in buffer. */
        buffer_flush(output_file, header_begin);

        if (buffer_len < header_len) {
            /* Empty buffer or possible incomplete header, buffer more data and
             * try again. */
            if (buffer_replenish(input_file) == 0) {
                /* Nothing new was read and no section header in buffer, flush
                 * remaining bytes and return. */
                buffer_flush(output_file, buffer_len);
                return;
            }
            continue;
        }

        /* Beginning of header found; discard header bytes and return */
        buffer_flush(NULL, header_len);
        return;
    }
}

static char *write_data_until_next_section(FILE *input_file, FILE *output_file)
{
    write_data_until_header_beginning(input_file, output_file);
    if (buffer_len == 0) {
        /* No more sections in the input file, we're done. */
        return NULL;
    }

    buffer_replenish(input_file);
    if (buffer_len == 0) {
        /* Malformed rich core - no header end. */
        return NULL;
    }

    size_t header_end = find_substring(buffer, buffer_len,
            RICHCORE_HEADER_END, RICHCORE_HEADER_END_LEN);
    if (header_end >= (buffer_len - RICHCORE_HEADER_END_LEN)) {
        /* Suspiciously long header, break. */
        return NULL;
    }

    char *header = malloc(header_end + 1);
    strncpy(header, buffer, header_end);
    header[header_end] = '\0';

    buffer_flush(NULL, header_end + RICHCORE_HEADER_END_LEN);

    return header;
}

static void extract_rich_core(FILE *input_file, const char *output_dir)
{
    FILE *output_file = fopen("/dev/null", "w");
    char *next_section;

    while ((next_section = write_data_until_next_section(input_file, output_file))) {
        fclose(output_file);

        char *file_name = basename(next_section);
        char file_path[128];

        snprintf(file_path, sizeof (file_path), "%s/%s", output_dir, file_name);
        output_file = fopen(file_path, "w");

        free(next_section);
    }

    fclose(output_file);
}

int main(int argc, char *argv[])
{
    char *input_fn;
    char *output_dir;
    struct stat stat_s;
    FILE *input_file;
    char buf[4096];

    if (argc < 2)
    {
        fprintf(stderr, usage, argv[0]);
        exit(1);
    }

    input_fn = argv[1];
    if (argc < 3)
    {
        /* check if filename ends with .rcore or .rcore.lzo */
        char *suffix = strstr(input_fn, ".rcore");

        if (!suffix || (strcmp(suffix, ".rcore.lzo") && strcmp(suffix, ".rcore")))
        {
            fprintf(stderr, "please specify output directory\n");
            exit(1);
        }

        if (!strcmp(suffix, ".rcore"))
            output_dir = strndup( input_fn, strlen(input_fn)-6 );
        else
            output_dir = strndup( input_fn, strlen(input_fn)-10 );
    }
    else
    {
        output_dir = argv[2];
    }

#ifdef DEBUG
    fprintf(stderr, "input: '%s'\n", input_fn);
    fprintf(stderr, "output: '%s'\n", output_dir);
#endif

    if (stat(input_fn, &stat_s))
    {
        fprintf(stderr, "input file error: %s\n", strerror(errno));
        exit(1);
    }

    if (S_ISDIR(stat_s.st_mode))
    {
        fprintf(stderr, "%s is a directory\n", input_fn);
        exit(1);
    }

    if (stat(output_dir, &stat_s))
    {
        if (errno != ENOENT)
        {
            fprintf(stderr, "error testing output: %s\n", strerror(errno));
            exit(1);
        }
    }
    else
    {
        fprintf(stderr, "%s exists, aborting\n", output_dir);
        exit(1);
    }

    if (mkdir(output_dir, 0777))
    {
        fprintf(stderr, "error creating %s: %s\n", output_dir, strerror(errno));
        exit(1);
    }

    snprintf(buf, 255, "lzop -d -c \"%s\"", input_fn);
    input_file = popen(buf, "r");
    if (!input_file)
    {
        fprintf(stderr, "error forking lzop: %s\n", strerror(errno));
        exit(1);
    }

    extract_rich_core(input_file, output_dir);

    pclose(input_file);

    exit(0);
}
