# Remaining Fixes for Boardify

## Issues to Fix:

### 1. Dashboard Not Showing Boards
- **Problem**: Boards list is empty on homepage after creation
- **Solution**: The API endpoint `/api/boards` should return both owned and invited boards
- **Status**: Backend looks correct, need to debug frontend console

### 2. Activity Log Position
- **Problem**: Activity log needs to be at the bottom of board page
- **Current**: Already at bottom in board.html template
- **Check**: Verify it's visible and scrollable

### 3. Calendar Not Highlighting Due Dates
- **Problem**: Calendar should show tasks with due dates highlighted
- **Backend**: `/api/users/me/calendar` endpoint exists
- **Frontend**: profile.js loads calendar tasks
- **Check**: Verify tasks with due_date are being returned

### 4. My Tasks Tab Empty
- **Problem**: Assigned tasks not showing in profile
- **Backend**: `/api/users/me/tasks` endpoint exists
- **Issue**: May need to check if assignments are being created properly
- **Check**: Verify CardAssignment records are created when assigning users

### 5. No Notifications for Invites/Assignments
- **Problem**: Users don't know when they're invited or assigned
- **Solution Needed**: 
  - Add notifications table to database
  - Create notification system
  - Show notifications in navbar
  - Send notifications when:
    - User is invited to board
    - User is assigned to card
    - Card due date is approaching

## Quick Debug Steps:

1. Open browser console (F12) on dashboard
2. Check if `/api/boards` returns data
3. Check if boards array has items
4. Verify session is active

## Test the following:
- Create a board → Go back to homepage → Should see the board
- Invite a user → They should see the board on their homepage
- Assign a user to a card → Check /profile → Should see in "My Tasks"
- Set due date on assigned card → Check calendar → Should be highlighted
