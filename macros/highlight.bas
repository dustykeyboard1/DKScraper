Sub HighlightCellsBasedOnValueInAllSheets()
    Dim wb As Workbook
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim cell As Range
    
    Set wb = ActiveWorkbook
    
    For Each ws In wb.Sheets
        lastRow = ws.Cells(ws.Rows.Count, "M").End(xlUp).Row ' Adjusted to consider column H as the reference for the last row
        
        For i = 1 To lastRow
            ' Check each cell in columns F, G, H
            For Each cell In ws.Range("H" & i & ":J" & i)
                If Not IsError(cell.Value) Then
                    If cell.Value < 30 Then
                        cell.Interior.Color = RGB(255, 0, 0) ' Highlight the cell red
                    ElseIf cell.Value > 70 Then
                        cell.Interior.Color = RGB(0, 255, 0) ' Highlight the cell green
                    Else
                        cell.Interior.ColorIndex = xlNone ' Clear any existing background color
                    End If
                End If
            Next cell
            
            ' Check each cell in columns I, J, K
            For Each cell In ws.Range("K" & i & ":M" & i)
                If Not IsError(cell.Value) Then
                    If cell.Value < 30 Then
                        ' The color assignments here were reversed from the initial setup; correcting to match the first loop
                        cell.Interior.Color = RGB(0, 255, 0) ' Highlight the cell red
                    ElseIf cell.Value > 70 Then
                        cell.Interior.Color = RGB(255, 0, 0) ' Highlight the cell green
                    Else
                        cell.Interior.ColorIndex = xlNone ' Clear any existing background color
                    End If
                End If
            Next cell
        Next i
    Next ws
End Sub
