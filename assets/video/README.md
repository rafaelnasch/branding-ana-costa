# Kit de vídeo · Ana Paula Costa · Nutricionista

Abertura (2,5 s), encerramento (2,5 s), encerramento curto (1 s) e lower third, em MP4 H.264 com o fundo da marca e em MOV Apple ProRes 4444 com transparência, nos formatos 1080 × 1920 e 1920 × 1080, a 30 quadros por segundo. Cada vídeo tem um PNG com o quadro final.

O passo a passo de uso (CapCut, Premiere, DaVinci, Final Cut), a legenda, o ajuste de cor e a zona segura estão em [`../producao/README.md`](../producao/README.md).

Os arquivos são gerados por `python3 tools/kit_video.py` a partir dos SVG oficiais. Enquanto o número do CRN-4 não chega (pendência P1), as peças trazem "CRN-4 em confirmação" e não vão a público.

Encerramento: logotipo vertical (símbolo, nome e "Nutricionista") com a linha do CRN, em Mar Fundo, Sálvia Ana, Algodão e Bruma. Fundo pela fase: Bruma na gestação, Algodão no pós-parto, Mar Fundo no 40+. Cada encerramento tem uma versão `-sem-crn.mp4`; os PNG `encerramento/crn-sobreposicao-*.png` trazem só a linha do CRN na posição certa, para pôr por cima quando o número chegar (ou rode `python3 tools/kit_video.py --crn "CRN-4 00000"`).
