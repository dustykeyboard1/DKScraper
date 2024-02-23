Sub MergeTeamRowsAndRemoveNA()
    Dim wb As Workbook
    Set wb = ThisWorkbook ' Use the workbook where the macro is running.
    
    Dim ws As Worksheet
    Dim i As Long
    Dim lastRow As Long
    Dim teamName As String
    Dim startRow As Long
    
    ' Loop through each sheet in the workbook
    For Each ws In wb.Sheets
        With ws
            ' Remove rows with "N/A" in Column C
            lastRow = .Cells(.Rows.Count, "C").End(xlUp).Row
            For i = lastRow To 2 Step -1
                If .Cells(i, "C").Value = "N/A" Then
                    .Rows(i).Delete
                End If
            Next i

            ' Refresh the last row after deletion
            lastRow = .Cells(.Rows.Count, "B").End(xlUp).Row

            ' Loop from the last row up to the second row
            For i = lastRow To 2 Step -1
                ' Check if the team name changes
                If .Cells(i, "B").Value <> .Cells(i - 1, "B").Value Then
                    ' Insert a new row for the team header
                    .Rows(i).Insert Shift:=xlDown, CopyOrigin:=xlFormatFromLeftOrAbove
                    teamName = .Cells(i + 1, "B").Value
                    ' Set the team name and merge cells from C to K
                    .Cells(i, "C").Value = teamName
                    .Cells(i, "C").HorizontalAlignment = xlCenter
                    .Cells(i, "C").VerticalAlignment = xlCenter
                    .Range(.Cells(i, "C"), .Cells(i, "M")).Merge
                    .Range(.Cells(i, "C"), .Cells(i, "M")).Font.Bold = True
                End If
            Next i
            
            ' Delete the "Teams" column
            .Columns("B").Delete
        End With
    Next ws
End Sub
