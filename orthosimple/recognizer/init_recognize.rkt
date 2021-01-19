#! /usr/bin/env racket

#lang racket

(require "recognize.rkt")

(define (setupConnection) 
  (define local_ip "127.0.0.1")
  (define listener (tcp-listen 43938))
  (define-values (inPort outPort) (tcp-accept listener))
  (define out-writer (port-write-handler outPort))

  (define get-second-unquoted (lambda (unquoted-lst)
                                (second (second unquoted-lst))))
  
  (define (recognize-strokes)
    (define points-lst (read inPort))
    (cond
      [(eof-object? points-lst)
       (tcp-close listener)]
      [else (define output-identifiers
              (two-stroke-rec (generate-lst (first points-lst))
                              (generate-lst (get-second-unquoted points-lst)) 10))

            (write (~a (string-join (map symbol->string output-identifiers) " ")
                       #:min-width 14) ; two chars for quotes 
                   outPort)
            (flush-output outPort)
            (recognize-strokes)]))

  ;; (generate-lst input-lst) produces a racket list of points corresponding to
  ;; a list of points separated by unquotes.
  (define (generate-lst input-lst)
    (define generate-pair (lambda (pair-input)
                            (list (first pair-input)
                                  (get-second-unquoted pair-input))))
    (cons (generate-pair (first input-lst))
          (map (lambda (unquote-pair)
                 (generate-pair (second unquote-pair))) (rest input-lst))))
  
  (recognize-strokes))

(setupConnection )