# Simple Ballot
A Simple Balloting System that balance weight and chance.

https://user-images.githubusercontent.com/42031070/163808861-23625efe-0743-46c5-8ce0-863e29a3cfff.mp4

---

## Quick Start

Example ballot applicant list can be found [here](https://github.com/spydermaxi/simple-ballot/blob/main/test/applicants.csv).

The condition is to balance the chance for the amount of tickets that they are trying to ballot for.
The more ticket amount, the lesser the chance during ballot.

1. Import code

   ```python

   from simple_ballot import ballot

   ```

2. Execute code

   ```python
   output = ballot.run_ballot(input_path=r"test\applicants.csv", total_resource=30)
   ```

3. Input required information / acknowledgements

   a. If found columns with unique identities, acknowledgement by user. If none found, will auto generate.

      ```bash
      Checking Columns for unique identities
      Found unique column - Employee ID, Use this?[Y/n] Y
      ```

   b. Select the column that holds the weight or quantity of the resource

      ```bash
      =============List of columns in your dataframe==============
      | Index | Column Name |
      | 0     | Name        |
      | 1     | Employee ID |
      | 2     | Tickets Qty |
      Please select the weight column (enter index no.): 2
      ```

      ``Ticket Qty`` is selected in this case, ``2`` is entered

   c. Select 1.Equal Chance or 2.Weighted Chance
      In weight chance, the more weights will get less chance and the less weights will get more chances

      ```bash
      Select 1.Equal Chance or 2.Weighted Chance: 2
      ```

      ``2`` was selectec

4. The ballot will start and STDOUT is displayed

   ```bash
   ========================Draw Starts=========================
   629364 has won 2 ticket
   643973 has won 1 ticket
   632384 has won 2 ticket
   635492 has won 1 ticket
   623345 has won 3 ticket
   623453 has won 5 ticket
   643234 has won 1 ticket
   623343 has won 4 ticket
   639809 has won 2 ticket
   648789 has won 3 ticket
   638405 has won 6 ticket
   =========================Draw Ended=========================
   Out of 30 ticket(s), remains 0 ticket(s)
   ============================================================
   ====================Winning Participants====================
          Name Employee ID  Tickets Qty
   1       Ben      629364            2
   6    Gerald      643973            1
   7     Harry      632384            2
   0       Amy      635492            1
   8       Ivy      623345            3
   10     Kyle      623453            5
   12    Mandy      643234            1
   15     Fred      623343            4
   13   Nathan      639809            2
   14  Charlie      648789            3
   5      Fred      638405            6
   ===================Remaining Participants===================
          Name Employee ID  Tickets Qty
   2   Charlie      639405            3
   3   Derrick      630484            4
   4     Eason      629374            5
   9       Jay      634253            4
   11      Ben      624354            6
   16    Sally      623455            5
   17      Zoe      633333            6
   ============================================================
   ```

---

## Example use case
Given a balloting campaign where the objective is to decide the allocation of carnival tickets to applicants by drawing lots.

1. There is a limited amount of carnival tickets up for grabs
2. Only **ONE** application per applicant (applicant is uniquely identified)
3. Applicants can decide how many carnival tickets he/she would like if he/she wins the ballot (up to a specified limit)
4. Minimum 1 carnival ticket or up to maximum 6 carnival ticket (the specified limit)
5. Ballot conditions:

   a. Registered tickets and ballot chances:
   
      - 1 ticket requested (weight) = 6 ballot tickets (chances)
      - 2 tickets requested (weight) = 5 ballot tickets (chances)
      - 3 tickets requested (weight) = 4 ballot tickets (chances)
      - 4 tickets requested (weight) = 3 ballot tickets (chances)
      - 5 tickets requested (weight) = 2 ballot tickets (chances)
      - 6 tickets requested (weight) = 1 ballot ticket (chance)
      
   b. 1 chance = 1 ballot ticket, 6 chances = 6 ballot tickets

      > Example:
      > - Amy register 2 tickets =  gives her 4 ballot tickets
      > - Ben register 6 tickets = gives him 1 ballot tickets
      > - Charlie register 1 ticket = gives him 5 ballot tickets
      > - During ballot, there are total 10 ballot tickets, obviously Charlie gets more chance to win.
      > - If Charlie won, we will remove all his ballot tickets to prevent redraw.

   c. This will balance the utilization and encourage more wide spread participation.

---

This repo is still work in progress. For any contribution, kindly submit and issue and pull request.

Thanks!
