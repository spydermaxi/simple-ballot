# Simple Ballot
A Simple Balloting System that balance weight and chance.

---

## Example use case
Given a balloting campaign where the objective is to decide the allocation of carnival tickets to applicants by drawing lots.

1. There is a limited amount of carnival tickets up for grabs
2. Only **ONE** application per applicant (applicant is uniquely identified)
3. Applicants can decide how many carnival tickets he/she would like if he/she wins the ballot (up to a specified limit)
4. Minimum 1 carnival ticket or up to maximum 6 carnival ticket (the specified limit)
5. Ballot conditions:

   a. Registered tickets and ballot chances:
   
      - 1 ticket requested (weight) = 5 ballot tickets (chances)
      - 2 tickets requested (weight) = 4 ballot tickets (chances)
      - 3 tickets requested (weight) = 3 ballot tickets (chances)
      - 4 tickets requested (weight) = 2 ballot tickets (chances)
      - 5/6 tickets requested (weight) = 1 ballot ticket (chance)
      
   b. 1 chance = 1 ballot ticket, 6 chances = 6 ballot tickets

      > Example:
      > - Amy register 2 tickets =  gives her 4 ballot tickets
      > - Ben register 6 tickets = gives him 1 ballot tickets
      > - Charlie register 1 ticket = gives him 5 ballot tickets
      > - During ballot, there are total 10 ballot tickets, obviously Charlie gets more chance to win.
      > - If Charlie won, we will remove all his ballot tickets to prevent redraw.

   c. This will balance the utilization and encourage more wide spread participation.
