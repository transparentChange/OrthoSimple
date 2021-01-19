#lang racket

(provide spatial-rec)
(provide two-stroke-rec)

(require rackunit)
(require "gesture_associations.rkt")

;; A Point is a (list Num Num)

;; A Gesture is a (listof (list Num Num))

;; A BoundingBox (BB) is a (list Point Point)
;; requires: the coordinate values in the first point are less than the
;;             respective values in the second point

;; A TemplateLibrary (TL) is a (listof (list Sym Gesture))
;; requires: the list is non-empty
;;           each Sym key is unqiue
;;           each Gesture value is not both vertical and horizontal
       

(define five-sample-length 5)
(define tolerance 0.01) ; for testing

;; (get-x point) produces the x-coordinate of point
;; get-x: Point -> Num
(define (get-x point)
  (first point))

;; (get-y point) produces the y-coordinate of point
;; get-y: Point -> Num
(define (get-y point)
  (second point))


;; (get-b-box gesture) produces the gesture's Bounding Box, i.e. produces the
;; smallest Bounding Box that encompasses all of the Points in gesture

;; get-b-box: Gesture -> BB
;; Requires:
;;     gesture is non-empty
(define (get-b-box gesture)
  ;; (get-box-from-first gesture first-x first-y) produces the gesture's Bounding
  ;; Box, i.e. produces the smallest Bounding Box that encompasses all of the
  ;; Points in gesture, in such a way that the Point with coordinates first-x,
  ;; first-y is contained in the Bounding Box
  ;; get-box-from-first: Gesture Num Num -> BB
  (define (get-box-from-first gesture first-x first-y)
    (get-box-from-maxmin gesture first-x first-y first-x first-y))

  ;; (get-box-from-maxmin gesture min-x min-y max-x max-y) produces the gesture's
  ;; Bounding Box, i.e. produces the smallest Bounding Box that encompasses all
  ;; of the Points in gesture, keeping track of the top-left and bottom-right
  ;; Points of the Bounding Box with the coordinates min-x, min-y and
  ;; max-x, max-y.
  ;; get-box-from-maxmin: Gesture Num Num Num Num -> BB
  (define (get-box-from-maxmin gesture min-x min-y max-x max-y)
    (cond
      [(empty? gesture) (list (list min-x min-y)
                              (list max-x max-y))]
      [else (get-box-from-maxmin (rest gesture)
                                 (min min-x (get-x (first gesture)))
                                 (min min-y (get-y (first gesture)))
                                 (max max-x (get-x (first gesture)))
                                 (max max-y (get-y (first gesture))))]))
  
  (get-box-from-first (rest gesture)
                      (get-x (first gesture))
                      (get-y (first gesture))))

;; Tests:
(check-equal? (get-b-box (list (list 10 0) (list 20 10) (list 30 20)
                               (list 30 30) (list 10 30) (list 0 0)))
              (list (list 0 0) (list 30 30)))
(check-equal? (get-b-box (list (list 5 5) (list 10 5) (list 5 10) (list 0 5)))
              (list (list 0 5) (list 10 10))) 


;; (gesture-length gesture) produces the length of the gesture, that is,
;; the sum of the distances between each pair of adjacent Points in gesture.
;; If gesture is empty or is composed of one Point, produces 0.
;; gesture-length: Gesture -> Num
(define (gesture-length gesture)
  ;; (non-empty-gesture-length gesture) produces the length of the gesture, that
  ;; is the sum of the distances between each pair of adjacent Points in gesture.
  ;; If gesture is composed of one Point, produces 0.
  ;; non-empty-gesture-length: Gesture -> Num
  ;; Requires:
  ;;     gesture is non-empty
  (define (non-empty-gesture-length gesture)
    (cond
      [(empty? (rest gesture)) 0]
      [else (+ (distance-between-points (first gesture)
                                        (second gesture))
               (non-empty-gesture-length (rest gesture)))]))

  (cond
    [(empty? gesture) 0]
    [else (non-empty-gesture-length gesture)]))

;; (distance-between-points point1 point2) produces the distance between point1
;; and point2 in R^2.
;; distance-between-points: Point Point -> Num
(define (distance-between-points point1 point2)
  (expt (+ (sqr (- (get-x point1)
                   (get-x point2)))
           (sqr (- (get-y point1)
                   (get-y point2))))
        0.5))

;; Tests:
(check-equal? (gesture-length empty) 0)
(check-equal? (gesture-length (list (list 5 2))) 0)
(check-equal? (gesture-length (list (list 1 1) (list 2 1) (list 2 2)
                                    (list 1 2) (list 1 1)))
              4)
(check-equal? (gesture-length (list (list 3 3) (list 3 3))) 0)
(check-within (gesture-length (list (list 2 -1) (list 1 -2) (list 2 -1)))
              (* 2 (expt 2 0.5)) tolerance)


;; (get-points gesture indices-list) produces a Gesture made up of Points from
;; gesture with index specified by each number in indices-list. Order is
;; maintained. 
;; get-points: Gesture (listof Nat) -> Gesture
;; Requires:
;;   * gesture is non-empty
;;   * indices-list is non-decreasing
;;   * every number in indices-list belongs to the set {0, 1, ..., (n - 1)},
;;     where n is the number of points in gesture  
(define (get-points gesture indices-list)
  
  ;; (get-points-by-index gesture indices-list cur-index) produces a Gesture made
  ;; up of Points from gesture with index specified by each number in
  ;; indices-list. Order is maintained. cur-index keeps track of the index
  ;; in gesture that is being compared with (first indices-list). It should be
  ;; initialized to 0.
  ;; get-points-by-index: Gesture (listof Nat) Nat -> Gesture
  ;; Requires:
  ;;   * gesture is non-empty
  ;;   * indices-list is non-decreasing
  ;;   * every number in indices-list belongs to the set {0, 1, ..., (n - 1)},
  ;;     where n is the number of points in gesture
  ;;   * cur-index <= (first indices-list)
  (define (get-points-by-index gesture indices-list cur-index)
    (cond
      [(empty? indices-list) empty] ; if gesture is empty, so is indices-list
      [(< cur-index (first indices-list)) (get-points-by-index (rest gesture)
                                                             indices-list
                                                             (add1 cur-index))]
      [(= cur-index (first indices-list))
       (cons (first gesture)
             (get-points-by-index gesture
                                  (rest indices-list)
                                  cur-index))]))
  (get-points-by-index gesture indices-list 0))

;; Tests:
(define mygest (list (list 100 0) (list 200 100) (list 100 200)
                     (list 0 100) (list 100 50)))
(check-equal? (get-points (list (list 3 9)) empty) empty)
(check-equal? (get-points (list (list 9 3)) (list 0)) (list (list 9 3)))
(check-equal? (get-points (list (list 1 2) (list 3 4)) (list 0 0 1))
              (list (list 1 2) (list 1 2) (list 3 4)))
(check-equal? (get-points mygest (list 0 0 2 4 4))
              (list (list 100 0) (list 100 0) (list 100 200) (list 100 50)
                    (list 100 50))) ; sample
(check-equal? (get-points (list (list 4 5) (list 7 6)) (list 1 1 1))
              (list (list 7 6) (list 7 6) (list 7 6)))
(check-equal? (get-points (list (list 2 4) (list -3 -1) (list 0 0))
                          (list 0 1 1 2))
              (list (list 2 4) (list -3 -1) (list -3 -1) (list 0 0)))
(check-equal? (get-points (list (list 8 7) (list 0 12) (list -2 4)) (list 0 2))
              (list (list 8 7) (list -2 4)))
(check-equal? (get-points (list (list 0 0) (list 1 1) (list 2 2) (list 3 3)
                                (list 4 4))
                          (list 1 3))
              (list (list 1 1) (list 3 3)))
(check-equal? (get-points (list (list 8 7) (list 0 12) (list -2 4)) (list 0 2))
              (list (list 8 7) (list -2 4)))
(check-equal? (get-points (list (list 0 0) (list 1 1) (list 2 2) (list 3 3)
                                (list 4 4))
                          (list 1 3))
              (list (list 1 1) (list 3 3)))


;; (move-and-scale gesture x-scale y-scale) moves gesture to (0, 0) and
;; scales it by (x-scale)x(y-scale)
;; move-and-scale: Gesture Num Num -> Gesture
;; requires: gesture is non-empty
;;           x-scale > 0
;;           y-scale > 0
(define (move-and-scale gesture x-scale y-scale)
  ;; (scale-gesture gesture x-scale y-scale) produces the Gestrue obtained by
  ;; by scaling gesture by x-scale and y-scale such that each Point in
  ;; gesture ((list x y)) becomes (list (* x x-scale) (* y y-scale))
  ;; scale-gesture: Gesture Num Num -> Gesture
  ;; Requires:
  ;;     x-scale and y-scale strictly greater than 0
  (define (scale-gesture gesture x-scale y-scale)
    (cond
      [(empty? gesture) empty]
      [else (cons (list (* (get-x (first gesture))
                           x-scale)
                        (* (get-y (first gesture))
                           y-scale))
                  (scale-gesture (rest gesture) x-scale y-scale))]))
  
  ;; (translate-to-origin gesture b-box) produces the Gesture obtained by
  ;; translating gesture to the origin using the first Point of b-box, which
  ;; represents the gesture's Bounding Box.
  ;; translate-to-origin: Gesture BB -> Gesture
  ;; Requires:
  ;;     gesture is non-empty
  (define (translate-to-origin gesture b-box)
    (translate-gesture gesture
                       (- (get-x (first b-box)))
                       (- (get-y (first b-box)))))
  
  ;; (translate-gesture gesture x-offset y-offset) produces the Gesture obtained
  ;; by translating gesture by x-offset and y-offset such that each Point in
  ;; gesture ((list x y)) becomes (list (+ x x-offset) (+ y y-offset))
  ;; translate-gesture: Gesture Num Num -> Gesture
  (define (translate-gesture gesture x-offset y-offset)
    (cond
      [(empty? gesture) empty]
      [else (cons (list (+ (get-x (first gesture))
                           x-offset)
                        (+ (get-y (first gesture))
                           y-offset))
                  (translate-gesture (rest gesture) x-offset y-offset))]))
  
  (scale-gesture (translate-to-origin gesture (get-b-box gesture))
                 x-scale
                 y-scale))

;; Tests:
(check-equal? (move-and-scale (list (list 1 1)) 1 1) (list (list 0 0)))
(check-equal? (move-and-scale (list (list 1 5) (list 3 4)) 1 1)
              (list (list 0 1) (list 2 0)))
(check-within (move-and-scale (list (list 4 4) (list 4 8)) 0.2 0.5)
              (list (list 0 0) (list 0 2)) tolerance)
(check-within (move-and-scale (list (list 3 3) (list 9 3)) 0.5 1)
              (list (list 0 0) (list 3 0)) tolerance)
(check-equal? (move-and-scale (list (list 100 101) (list 101 102)) 3 1)
              (list (list 0 0) (list 3 1)))
(check-equal? (move-and-scale (list (list 5 5) (list 2 2)) 3 0.5)
              (list (list 9 1.5) (list 0 0)))
(check-equal? (move-and-scale (list (list 5 5)) 10 7) (list (list 0 0)))
(check-within (move-and-scale (list (list 4 1) (list 3.5 3) (list 3 4)) 1 1)
              (list (list 1 0) (list 0.5 2) (list 0 3)) tolerance)
(check-equal? (move-and-scale (list (list 2 2) (list 1 3) (list 2 4)) 2 3)
              (list (list 2 0) (list 0 3) (list 2 6)))


;; (normalize-gesture gesture) normalizes gesture to (0,0) and a standard size

;; normalize-gesture: Gesture -> Gesture
;; Requires:
;;     * gesture is not both vertical and horizontal
;;     * gesture is non-empty
(define (normalize-gesture gesture)
  (define min-width 20)
  (define min-height 20)
  (define norm-size 200)
  
  ;; (normalize-gesture-from-box gesture b-box) produces the Gesture that results
  ;; from moving it to the origin and scaling it to a standard dimension. It
  ;; does not scale an axis if the corresponding dimensions of the b-box, which
  ;; represents the Bounding Box of gesture, are less than min-width for the
  ;; width or min-height for the height.
  ;; normalize-gesture-from-box: Gesture BB -> Gesture
  ;; Requires:
  ;;     gesture is non-empty
  (define (normalize-gesture-from-box gesture b-box)
    (move-and-scale
     gesture
     (get-x-scale (- (get-x (second b-box))
                     (get-x (first b-box))))
     (get-y-scale (- (get-y (second b-box))
                     (get-y (first b-box))))))

  ;; (get-x-scale width) produces the value that a gesture with width should be
  ;; scaled by horizontally.
  ;; get-x-scale: Num -> Num
  (define (get-x-scale width)
    (cond
      #| min-width > 0, so division by zero never occurs in the second clause of
       the cond |#
      [(< width min-width) 1]
      [else (/ norm-size width)]))

  ;; (get-y-scale height) produces the value that a gesture with height should be
  ;; scaled by vertically.
  ;; get-y-scale: Num -> Num
  (define (get-y-scale height)
    (cond
      #| min-height > 0, so division by zero never occurs in the second clause of
       the cond |#
      [(< height min-height) 1]
      [else (/ norm-size height)]))
  
  (normalize-gesture-from-box gesture (get-b-box gesture)))

;; Tests:
(check-equal? (normalize-gesture (list (list 40 50) (list 80 90)))
              (list (list 0 0) (list 200 200)))
(check-equal? (normalize-gesture (list (list 80 90) (list 40 130)))
              (list (list 200 0) (list 0 200)))
(check-within (normalize-gesture (list (list 0 0) (list 100 100)))
              (list (list 0 0) (list 200 200)) tolerance)
(check-within (normalize-gesture (list (list 100 0) (list 100 50)
                                       (list 200 50)))
              (list (list 0 0) (list 0 200) (list 200 200)) tolerance)
(check-within (normalize-gesture (list (list 20 10) (list 80 5) (list 25 10)))
              (list (list 0 5) (list 200 0) (list 16.67 5)) tolerance)
(check-within (normalize-gesture (list (list 20 20) (list 220 300)
                                       (list 70 70)))
              (list (list 0 0) (list 200 200) (list 50 35.71)) tolerance)
(check-within (normalize-gesture (list (list 30 225) (list 130 25)
                                       (list 130 425) (list 230 225)))
              (list (list 0 100) (list 100 0) (list 100 200) (list 200 100))
              tolerance)


;; (sub-sample gesture num-points) produces a sampling of gesture containing
;; num-points Points, the element with index k being the element with index
;; (* k (/ (length gesture) (- num-points 1)) in gesture for k in
;; 0, ..., num-points - 2, and the last element being the last element in
;; gesture.
;; sub-sample: Gesture Nat -> Gesture
;; Requires:
;;     gesture is non-empty
;;     num-points > 2
(define (sub-sample gesture num-points)
  ;; (sub-sample-by-step gesture sum-steps index step) produces a sampling of
  ;; gesture with elements at index (floor sum) for each sum in sum-steps_k,
  ;; where sum-steps_k is defined by the relation: sum-steps_0 = 0,
  ;; sum-steps_k+1 = sum-steps_k + step for k >= 0 with the restriction that
  ;; sum-steps_i < (sub1 (length gesture)). index is a counter variable for the
  ;; index in gesture. Both index and sum-steps should be initialized to 0.  
  ;; sub-sample-by-step: Gesture Num Nat Num -> Gesture
  ;; Requires:
  ;;     gesture is non-empty
  (define (sub-sample-by-step gesture index sum-steps step)
    (cond
      #| the not clause is necessary to ensure sampling (excluding the last entry)
       is finished |#
      [(and (empty? (rest gesture))
            (not (= index (floor sum-steps)))) (cons (first gesture) empty)]
      
      [(= index (floor sum-steps)) (cons (first gesture)
                                         (sub-sample-by-step gesture
                                                             index
                                                             (+ sum-steps step)
                                                             step))]
      [(< index (floor sum-steps)) (sub-sample-by-step (rest gesture)
                                                       (add1 index)
                                                       sum-steps step)]))
  
  (sub-sample-by-step gesture 0 0 (/ (length gesture) (sub1 num-points))))

;; Tests:
(check-equal? (sub-sample (list (list 4 4) (list 5 5) (list 6 6)) 3)
              (list (list 4 4) (list 5 5) (list 6 6)))
(check-equal? (sub-sample (list (list 1 1) (list 3 3)) 4)
              (list (list 1 1) (list 1 1) (list 3 3) (list 3 3)))
(check-equal? (sub-sample (list (list 1 1) (list 3 3) (list 5 5) (list 7 7)
                                (list 2 2) (list 4 4) (list 6 6) (list 8 8)
                                (list 9 9) (list 0 9)) 8)
              (list (list 1 1) (list 3 3) (list 5 5) (list 2 2) (list 4 4)
                    (list 8 8) (list 9 9) (list 0 9)))
(check-equal? (sub-sample (list (list 2 3)) 3)
              (list (list 2 3) (list 2 3) (list 2 3)))
(check-equal? (sub-sample (list (list 1 1) (list 2 2) (list 3 3) (list 4 4)
                                (list 5 5) (list 6 6) (list 7 7) (list 8 8)) 5)
              (list (list 1 1) (list 3 3) (list 5 5) (list 7 7) (list 8 8)))
(check-equal? (sub-sample (list (list 10 9) (list 8 7) (list 6 5)) 7)
              (list (list 10 9) (list 10 9) (list 8 7) (list 8 7) (list 6 5)
                    (list 6 5) (list 6 5)))


;; (spatial-sub-sample gesture num-points) produces a Gesture that contains
;; num-points Points that are equally spaced out along the path of the original
;; gesture.
;; Examples:

;; spatial-sub-sample: Gesture Nat -> Gesture
;; Requires:
;;     gesture is non-empty
;;     num-points > 2     
(define (spatial-sub-sample gesture num-points)
  ;; (sample-from-standard-dist gesture standard-dist) produces a Gesture that is
  ;; made up of Points that are standard-dist distance apart along the original
  ;; gesture, starting from the first point.
  ;; sample-from-standard-dist: Gesture Num -> Gesture
  ;;     (gesture-length gesture) >= 2
  (define (sample-from-standard-dist gesture standard-dist)
    (cons (first gesture)
          (sample-from-distances (rest gesture)
                                 (distance-between-points (first gesture)
                                                          (second gesture))
                                 (get-x (first gesture))
                                 (get-y (first gesture))
                                 standard-dist standard-dist)))
  
  ;; (sample-from-distances gesture dist-to-next x-cur y-xur new-distance
  ;;  standard-dist) produces a Gesture that is made up of Points that are
  ;; standard-dist distance apart along the original gesture, starting
  ;; from, but not including, (x-cur, y-cur). dist-to-next represents the
  ;; distance to the next Point in the original gesture (which is also the first),
  ;; and new-distance represents the distance to the next Point in the Gesture
  ;; being produced.
  ;; sample-from-distances: Gesture Num Num Num Num Num -> Gesture
  (define (sample-from-distances gesture dist-to-next x-cur y-cur new-distance
                                 standard-dist)
    (cond
      [(empty? gesture) empty]
      [(< new-distance dist-to-next)
       (add-new-point (get-new-point x-cur (get-x (first gesture))
                                     y-cur (get-y (first gesture))
                                     (/ new-distance dist-to-next))
                      gesture
                    (- dist-to-next new-distance) standard-dist)]
      [(< (abs (- new-distance dist-to-next)) 1e-6)
       (add-new-point (cons (get-x (first gesture))
                            (cons (get-y (first gesture)) empty))
                      (rest gesture)
                      (calculate-dist-to-next gesture) standard-dist)] 
      [else (sample-from-distances
             (rest gesture)
             (calculate-dist-to-next gesture)
             (get-x (first gesture))
             (get-y (first gesture))
             (- new-distance dist-to-next)
             standard-dist)]))

  ;; (add-new-point new-point gesture dist-to-next standard-dist) produces a
  ;; Gesture that is made up of new-point and the result of calling
  ;; sample-from-distances with the expected arguments, except with
  ;; new-distance updated to standard-dist.
  ;; add-new-point: Point Gesture Num Num -> Gesture
  (define (add-new-point new-point gesture dist-to-next standard-dist)
    (cons new-point
          (sample-from-distances gesture
                                 dist-to-next
                                 (get-x new-point)
                                 (get-y new-point) 
                                 standard-dist standard-dist)))           
  
  ;; (calculate-dist-to-next gesture) produces the distance between the first and
  ;; second Points of gesture. Returns 0 if gesture is composed of one element.
  ;; calculate-dist-to-next: Gesture -> Num
  ;; Requires:
  ;;     gesture is non-empty
  (define (calculate-dist-to-next gesture)
    (cond
      [(empty? (rest gesture)) 0]
      [else (distance-between-points (first gesture)
                                     (second gesture))]))
  
  ;; (get-new-point x-cur x-next y-cur y-next proportion-interval)
  ;; produces the Point that is closer to the Point (x-next, y-next) from
  ;; (x-cur y-cur) by an amount that depends on proportion-interval.
  ;; get-new-point: Num Num Num Num Num -> Point
  ;; Requires:
  ;;     proportion-interval <= 1
  (define (get-new-point x-cur x-next y-cur y-next proportion-interval)
    (cons (get-new-coordinate x-cur x-next proportion-interval)
          (cons (get-new-coordinate y-cur y-next proportion-interval) empty)))
    
  ;; (get-new-coordinate cur-coordinate next-coordinate
  ;;  proportion-interval) produces the next coordinate that is closer to
  ;; next-coordinate from cur-coordinate by an amount that depends
  ;; proportion-interval.
  ;; get-new-coordinate: Num Num Num -> Num
  ;; Requires:
  ;;     0 < proportion-interval <= 1
  (define (get-new-coordinate cur-coordinate next-coordinate proportion-interval)
    (+ cur-coordinate
       (* proportion-interval
          (- next-coordinate cur-coordinate))))
  
  ;; (distance-between-coordinates x1 y1 x2 y2) produces the distance between
  ;; (x1, y1) and (x2, y2) in R^2.
  ;; distance-between-coordinates: Num Num Num Num -> Num
  (define (distance-between-coordinates x1 y1 x2 y2)
    (expt (+ (sqr (- x2 x1))
             (sqr (- y2 y1)))
          0.5))
  
  (cond
    [(empty? (rest gesture)) (sub-sample gesture num-points)] ; simple case
    [else (sample-from-standard-dist gesture
                                     (/ (gesture-length gesture)
                                        (sub1 num-points)))]))

;; Tests:
(check-equal? (spatial-sub-sample (list (list 2 2)) 4)
              (list (list 2 2) (list 2 2) (list 2 2) (list 2 2)))
(check-within (spatial-sub-sample (list (list 5 0) (list 0 5)) 3)
              (list (list 5 0) (list 2.5 2.5) (list 0 5)) tolerance)
(check-equal? (spatial-sub-sample (list (list 0 0) (list 2 0) (list 2 2)
                                        (list 0 2)) 4)
              (list (list 0 0) (list 2 0) (list 2 2) (list 0 2)))
(check-within (spatial-sub-sample (list (list 0 0) (list 2 0) (list 2 2)
                                        (list 0 2)) 7)
              (list (list 0 0) (list 1 0) (list 2 0) (list 2 1) (list 2 2)
                    (list 1 2) (list 0 2)) tolerance)
(check-within (spatial-sub-sample (list (list 0 0) (list 1 0) (list 2 0)
                                        (list 1 1) (list 0 2) (list 1 2)
                                        (list 2 2)) 3)
              (list (list 0 0) (list 1 1) (list 2 2)) tolerance)


;; (geometric-match-spatial gesture1 gesture2 num-sample-points) produces the
;; average distance between points in sub-sampled gesture1 and gesture2 after
;; sub-sampling them with num-sample-points Points
;; geometric-match-spatial: Gesture Gesture Nat -> Num
;; Requires:
;;     gesture1 and gesture2 are each not both vertical and horizontal
;;     gesture1 and gesture2 are non-empty
;;     num-sample-points > 2
(define (geometric-match-spatial gesture1 gesture2 num-sample-points)
  ;; (distance-between-gesture-points gesture1 gesture2) produces the sum of
  ;; the distances between the Points in gesture1 and gesture2 with the same
  ;; indices. We define the (distance-between-gesture-points empty empty) to be
  ;; 0.
  ;; distance-between-gesture-points: Gesture Gesture -> Num
  ;; Requires:
  ;;     gesture1 and gesture2 are of the same length
  (define (distance-between-gesture-points gesture1 gesture2)
    (cond
      [(empty? gesture1) 0]
      [else (+ (distance-between-points (first gesture1)
                                        (first gesture2))
               (distance-between-gesture-points (rest gesture1)
                                                (rest gesture2)))]))
  
  (/ (distance-between-gesture-points
      (normalize-gesture (sub-sample gesture1 num-sample-points))
      (normalize-gesture (sub-sample gesture2 num-sample-points)))
     num-sample-points))

;; Tests:
(check-within (geometric-match-spatial (list (list 0 200) (list 200 0))
                               (list (list 0 200) (list 0 100) (list 200 100)
                                     (list 200 0)) 3)
              33.33 tolerance)
(check-within (geometric-match-spatial (list (list 100 0) (list 100 200)
                                             (list 0 100)
                                      (list 200 100) (list 100 0))
                                (list (list 100 0) (list 100 200) (list 0 100)
                                      (list 200 100) (list 100 200)
                                      (list 200 200)) 5)
              169.44 tolerance)
(check-within (geometric-match-spatial
               (list (list 200 0) (list 100 0) (list 0 0)
                     (list 0 100) (list 100 100) (list 0 100)
                     (list 0 200) (list 100 200) (list 200 200))
               (list (list 200 0) (list 100 0) (list 50 50)
                     (list 0 100) (list 100 100) (list 0 100)
                     (list 50 150) (list 100 200)
                     (list 200 200)) 7)
              10.10 tolerance)                  

;; (spatial-rec candidate template-library num-sample-points) produces the
;; symbol in template-library closest to candidate.
;; Examples:
;; spatial-rec Gesture TL Nat -> Sym
;; Requires:
;;     candidate is not both vertical and horizontal
;;     candidate is non-empty
;;     num-sample-points > 2
(define (spatial-rec candidate template-library num-sample-points)
  ;; (closest-symbol-geometric-match-spatial candidate template-library
  ;;  num-points) produces a list containing the symbol in template-library
  ;; closest to candidate and the average distance between the points of
  ;; candidate and the Gesture that the symbol represents as produced by the
  ;; geometric-match function.
  ;; closest-symbol-geometric-match-spatial: Gesture TL Nat -> (list Sym Num)
  ;; Requires:
  ;;     candidate is not both vertical and horizontal
  ;;     candidate is non-empty
  ;;     num-sample-points > 2
  (define (closest-symbol-geometric-match-spatial candidate template-library
                                                  num-sample-points) 
    (cond
      [(empty? (rest template-library))
       (symbol-with-spatial-match candidate (first template-library)
                                  num-sample-points)]
      [else
       
       ;(writeln (symbol-with-spatial-match candidate (first template-library)
        ;                                   num-sample-points))
       (min-list-by-second      
             (symbol-with-spatial-match candidate (first template-library)
                                        num-sample-points)
             (closest-symbol-geometric-match-spatial candidate
                                                     (rest template-library)
                                                     num-sample-points))]))
  
  ;; (symbol-with-spatial-match candidate template-library-entry
  ;;                              num-sample-points) produces a list of length
  ;; two containing the first element of template-library-entry as its first
  ;; element and the average distance between the points of candidate and the
  ;; second element of template-library-entry as produced by the geometric-match
  ;; function.
  ;; symbol-with-spatial-match: Gesture (list Sym Gesture) Nat -> (list Sym Num)
  ;; Requires:
  ;;     candidate is not both vertical and horizontal
  ;;     candidate is non-empty
  ;;     num-sample-points > 2
  (define (symbol-with-spatial-match candidate template-library-entry
                                     num-sample-points)
    (list (get-symbol template-library-entry)
          (geometric-match-spatial candidate
                                   (get-gesture template-library-entry)
                                   num-sample-points)))
  
  ;; (min-list-by-second lst1 lst2) produces the list from the {lst1, lst2}
  ;; with the smaller second entry.
  ;; min-list-by-second: (listof Any) (listof Any) -> (listof Any)
  ;; Requires:
  ;;     The second elements of lst1 and lst2 are of type Num. This implies that
  ;;     lst1 and lst2 are both of at least length 2.
  (define (min-list-by-second lst1 lst2)
    (cond
      [(< (second lst1) (second lst2)) lst1]
      [else lst2]))
  
  ;; (get-gesture template-library-entry) produces the second element of
  ;; template-library-entry, which represents the Gesture associated with the
  ;; first element of template-library-entry.
  ;; get-gesture: (list Sym Gesture) -> Gesture
  ;; Requires:
  ;;     second element of template-library-entry is non-empty
  ;;     second element of template-library-entry is not both vertical and
  ;;     horizontal
  (define (get-gesture template-library-entry)
    (second template-library-entry))

  ;; (get-symbol template-library-entry) produces the first element of
  ;; template-library-entry, the Symbol which represents template-library-entry.
  ;; get-symbol: (list Sym Gesture) -> Sym
  ;; Requires:
  ;;     second element of template-library-entry is non-empty
  ;;     second element of template-library-entry is not both vertical and
  ;;     horizontal
  (define (get-symbol template-library-entry)
    (first template-library-entry))
  
  (first (closest-symbol-geometric-match-spatial candidate template-library
                                                 num-sample-points)))

;; Tests:
(check-equal? (spatial-rec
               (list (list 0 200) (list 200 0))
               (list
                (list 'corner (list (list 0 200) (list 0 0) (list 200 0)))
                (list 'elbows (list (list 0 200) (list 0 100) (list 200 100)
                                    (list 200 0)))
                (list 'zigzag (list (list 0 200) (list 100 100) (list 100 200)
                                    (list 200 0)))) 3)
              'elbows)
(check-equal? (spatial-rec
               (list (list 200 0) (list 100 0) (list 0 0)
                     (list 0 100) (list 100 100) (list 0 100)
                     (list 0 200) (list 100 200) (list 200 200))
               (list
                (list 'greater-than (list (list 200 0) (list 0 100)
                                          (list 200 200)))
                (list 'sigma (list (list 200 50) (list 200 0) (list 0 0)
                                   (list 100 100) (list 0 200) (list 200 200)
                                   (list 200 150)))
                (list 'lowercase-e (list (list 200 0) (list 100 0) (list 50 50)
                                         (list 0 100) (list 100 100)
                                         (list 0 100) (list 50 150)
                                         (list 100 200) (list 200 200)))) 6)
              'lowercase-e)


;; (two-stroke-rec gesture1 gesture2 num-sample-points) produces the letter and
;; the accent corresponding to gesture1 and gesture2 as determined by
;; spacial-rec, in the order depending on the gestures' respective lengths.
;; num-sample-points is passed along to spacial-rec, which produces the closest
;; gesture using samples of num-sample-points.
;; two-stroke-rec: Gesture Gesture Nat -> (list Symbol Symbol)
(define (two-stroke-rec gesture1 gesture2 num-sample-points)
  (define min-length 5)
  (define len1 (gesture-length gesture1))
  (define len2 (gesture-length gesture2))
  
  (define (two-id-lst letter-stroke accent-stroke)
    (list (spatial-rec letter-stroke letters num-sample-points)
          (cond
            [(or (<= len1 min-length)
                 (<= len2 min-length)) 'trema]
            [else (spatial-rec accent-stroke accents num-sample-points)])))
  
  (cond
    [(>= (gesture-length gesture1) (gesture-length gesture2))
     (two-id-lst gesture1 gesture2)]
    [else (two-id-lst gesture2 gesture1)]))

  
