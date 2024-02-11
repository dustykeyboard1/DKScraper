Attribute VB_Name = "Module1"
Sub FormatSheetAndRemoveNA()
    Dim ws As Worksheet
    Set ws = ActiveSheet
    
    Dim i As Long
    Dim lastRow As Long
    Dim teamName As String
    
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.DisplayAlerts = False

    ws.Columns("B").Delete Shift:=xlToLeft
    ' Find the last row of the sheet
    lastRow = ws.Cells(ws.Rows.Count, "B").End(xlUp).Row
    
    ' Loop from bottom to top
    For i = lastRow To 1 Step -1
        ' Check for team name indicator - "N/A" in the Player Name column (Column B)
        If IsEmpty(ws.Cells(i, "C").Value) Then
            ' Store the team name
            teamName = ws.Cells(i, "B").Value
            ' Delete the "N/A" row
            ws.Rows(i).Delete
            ' Insert a new row for the team name
            ws.Rows(i).Insert Shift:=xlDown
            ' Place the team name in the new row
            ws.Cells(i, "B").Value = teamName
            ' Merge the team name cells across the used range
            ws.Range(ws.Cells(i, "A"), ws.Cells(i, ws.UsedRange.Columns.Count)).Merge
            ' Format the team name row
            With ws.Cells(i, "B")
                .Font.Bold = True
                .HorizontalAlignment = xlCenter
            End With
            
        Else
            ws.Cells(i, "B").Delete Shift:=xlToLeft
        End If
    Next i
    
    ' Restore application settings
    Application.DisplayAlerts = True
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
End Sub


