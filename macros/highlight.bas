Sub HighlightCellsBasedOnValue()
    Dim ws As Worksheet
    Set ws = ActiveSheet
    
    Dim lastRow As Long
    Dim i As Long
    Dim cell As Range
    
    ' Find the last row with data in column G, H, or I
    lastRow = ws.Cells(ws.Rows.Count, "H").End(xlUp).Row
    
    ' Loop through all rows
    For i = 1 To lastRow
        ' Check each cell in columns G, H, and I
        For Each cell In ws.Range("F" & i & ":H" & i)
            If Not IsError(cell.Value) Then
                If cell.Value < 30 Then
                    ' Highlight the cell red
                    cell.Interior.Color = RGB(255, 0, 0) ' Red
                ElseIf cell.Value > 70 Then
                    ' Highlight the cell green
                    cell.Interior.Color = RGB(0, 255, 0) ' Green
                Else
                    ' Clear any existing background color if the value is between 30 and 70
                    cell.Interior.ColorIndex = xlNone
                End If
            End If
        Next cell
    Next i
End Sub
